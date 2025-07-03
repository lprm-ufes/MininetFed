from sklearn.cluster import AgglomerativeClustering
import sys
import random
from Pyfhel import Pyfhel, PyCtxt
import numpy as np
from sklearn.model_selection import KFold
import torchvision.transforms as transforms
from torch.utils.data import ConcatDataset
from torchvision.datasets import MNIST
import torch.optim as optim
import torch.nn as nn
import torch
import os
from .sketch_utils import compress, decompress, get_params, set_params, set_params_fedsketch, differential_garantee_pytorch, delta_weights, get_random_hashfunc
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


def recuperar_matriz_binaria(nome_arquivo, HE):
    """
    Recupera a matriz binária de um arquivo especificado, incluindo as chaves de linha, coluna e valor e considerando tamanhos variáveis de valores.

    Argumento:
      nome_arquivo: O nome do arquivo binário contendo a matriz.

    Retorna:
      A matriz binária recuperada (dicionário de dicionários).
    """
    matriz = {}

    with open(nome_arquivo, 'rb') as f:
        i = 0

        # Ler os bytes da matriz
        bytes_matriz = f.read()

        # Descodificar os bytes em elementos da matriz
        offset = 0
        while offset < len(bytes_matriz):
            i += 1

            # Ler o tamanho da chave linha1
            tamanho_chave_linha1 = int.from_bytes(
                bytes_matriz[offset:offset + 4], 'big')
            offset += 4
            # Ler os bytes da chave linha1
            bytes_chave_linha1 = bytes_matriz[offset:offset +
                                              tamanho_chave_linha1]
            offset += tamanho_chave_linha1
            # Decodificar a chave linha1 em string
            linha1 = bytes_chave_linha1.decode('utf-8')

            # Ler o tamanho da chave coluna1
            tamanho_chave_coluna1 = int.from_bytes(
                bytes_matriz[offset:offset + 4], 'big')
            offset += 4
            # Ler os bytes da chave coluna1
            bytes_chave_coluna1 = bytes_matriz[offset:offset +
                                               tamanho_chave_coluna1]
            offset += tamanho_chave_coluna1
            # Decodificar a chave coluna1 em string
            coluna1 = bytes_chave_coluna1.decode('utf-8')

            # Ler o tamanho do valor
            tamanho_valor = int.from_bytes(
                bytes_matriz[offset:offset + 4], 'big')
            offset += 4

            # Ler os bytes do valor
            bytes_valor = bytes_matriz[offset:offset + tamanho_valor]
            offset += tamanho_valor

            # Converter os bytes em PyCtxt e adicionar à matriz
            pyctxt_elemento = PyCtxt(pyfhel=HE, bytestring=bytes_valor)

            # Inserir o elemento na matriz usando as duas chaves
            matriz.setdefault(linha1, {})[coluna1] = pyctxt_elemento
    f.close()
    return matriz


def get_params(model):
    param_dict = {}
    for name, param in model.named_parameters():
        if param.requires_grad:
            param_dict[name] = param.clone()  # copy.deepcopy(param.clone())
    return param_dict


def set_params_fedsketch(model, data):
    for name, param in model.named_parameters():
        param.data = data[name]


class LeNet5(nn.Module):
    def __init__(self, num_classes, num_channels):
        super(LeNet5, self).__init__()
        self.layer1 = nn.Sequential(
            nn.Conv2d(1, 6*num_channels, kernel_size=5, stride=1, padding=0),
            nn.BatchNorm2d(6*num_channels),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2))
        self.layer2 = nn.Sequential(
            nn.Conv2d(6*num_channels, 16*num_channels,
                      kernel_size=5, stride=1, padding=0),
            nn.BatchNorm2d(16*num_channels),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2))
        self.fc = nn.Linear(400*num_channels, 120*num_channels)
        self.relu = nn.ReLU()
        self.fc1 = nn.Linear(120*num_channels, 84*num_channels)
        self.relu1 = nn.ReLU()
        self.fc2 = nn.Linear(84*num_channels, num_classes)

    def forward(self, x):
        out = self.layer1(x)
        out = self.layer2(out)
        out = out.reshape(out.size(0), -1)
        out = self.fc(out)
        out = self.relu(out)
        out = self.fc1(out)
        out = self.relu1(out)
        out = self.fc2(out)
        return out


class TrainerCkksfed():
    def __init__(self, ext_id, mode, id_name, args) -> None:
        self.args = args

        self.args['global_seed'] = 0
        CASE_SELECTOR = 1          # 1 or 2

        case_params = {
            1: {'l': 256},         # small l
            2: {'l': 65536},       # large l
        }[CASE_SELECTOR]
        self.l = case_params['l']

        self.id_name = id_name
        self.cluster_distance_threshold = 0.8
        self.cluster = []

        self.device = torch.device(
            'cuda' if torch.cuda.is_available() else 'cpu')
        dir_path = "temp/ckksfed_fhe/pasta"
        self.num_samples = 500
        self.num_tests = 250
        self.epochs = 1
        self.cost = nn.CrossEntropyLoss()
        self.learning_rate = 0.01
        self.metric_names = ["accuracy"]

        self.external_id = ext_id
        self.mode = mode  # client

        self.id = int(ext_id) + 1
        self.nc = self.id
        self.dataloader_train, self.dataloader_test = self.split_data()
        self.model = self.define_model()
        self.model_keys = list(get_params(self.model).keys())
        self.fedsketch = True  # Lembra de trocar no outro -------------------------
        if self.fedsketch:

            self.old_weights = get_params(self.model)
            self.weights = get_params(self.model)
            self.compression = 0.00066666666  # 75x
            self.length = 20
            self.desired_episilon = 1
            self.percentile = 90
            self.vector_length = sum(
                p.numel() for p in self.model.parameters() if p.requires_grad)
            self.index_hash_function = [get_random_hashfunc(
                _max=int(self.compression*self.vector_length), seed=repr(j).encode())
                for j in range(self.length)]

        self.stop_flag = False

        self.HE_f = Pyfhel()  # Empty creation
        self.HE_f.load_context(dir_path + "/context")
        self.HE_f.load_public_key(dir_path + "/pub.key")
        self.HE_f.load_secret_key(dir_path + "/sec.key")
        self.HE_f.load_relin_key(dir_path + "/relin.key")
        # self.HE_f.rotateKeyGen()
        # self.HE_f.load_rotate_key(dir_path + "/rotate.key")

    def encrypt_array(self, array):
        return [self.HE_f.encrypt(array[j:j+self.HE_f.get_nSlots()]) for j in range(0, self.l, self.HE_f.get_nSlots())]

    def encrypt_value(self, value):
        return self.HE_f.encrypt(value)

    def decrypt_value(self, value):
        return self.HE_f.decrypt(value)

    def decrypt_array(self, encrypted_array):
        out = np.array()
        for element in encrypted_array:
            decrypted_part = self.HE_f.decryptFrac(element)
            out = np.concatenate((out, decrypted_part))

        return out

    def set_args(self, args):
        self.args.update(args)

    def set_nc(self, clients):
        self.nc = clients

    def get_num_samples(self):
        return self.num_samples

    def define_model(self, n_channels=1, n_classes=10):
        # previous_seed = torch.initial_seed()
        # torch.manual_seed(self.args['global_seed'])
        model = LeNet5(n_classes, n_channels)
        # torch.manual_seed(previous_seed)
        return model

    def sample_random_dataloader(self, dataset, num_samples, batch_size):

        indices = torch.randperm(len(dataset))[:num_samples]
        sample = torch.utils.data.Subset(dataset, indices)
        # random_sampler = torch.utils.data.RandomSampler(dataset, num_samples=num_samples)
        dataloader = torch.utils.data.DataLoader(
            sample, batch_size=batch_size, shuffle=True, num_workers=2)
        # print(len(dataloader.dataset))

        return dataloader

    def split_data(self):
        # cliente
        train_dataset = MNIST(root='./data',
                              train=True,
                              transform=transforms.Compose([
                                  transforms.Resize((32, 32)),
                                  transforms.ToTensor(),
                                  transforms.Normalize(mean=(0.1307,), std=(0.3081,))]),
                              download=True)
        test_dataset = MNIST(root='./data',
                             train=False,
                             transform=transforms.Compose([
                                 transforms.Resize((32, 32)),
                                 transforms.ToTensor(),
                                 transforms.Normalize(mean=(0.1325,), std=(0.3105,))]),
                             download=True)

        if self.mode == "unbalanced-folds":
            possible_classes = [[1, 2], [3, 4], [5, 6], [7, 8]]
            classes = random.choice(possible_classes)
            self.classes = classes
            idx = (train_dataset.targets == classes[0]) | (
                train_dataset.targets == classes[1])
            train_dataset.targets = train_dataset.targets[idx]
            train_dataset.data = train_dataset.data[idx]
            # print(np.unique(train_dataset.targets))
            # print(train_dataset)
            idx = (test_dataset.targets == classes[0]) | (
                test_dataset.targets == classes[1])
            test_dataset.targets = test_dataset.targets[idx]
            test_dataset.data = test_dataset.data[idx]
            # print(np.unique(test_dataset.targets))
            # print(test_dataset)

            k_folds = 4
            dataset = ConcatDataset([train_dataset, test_dataset])
            kfold = KFold(n_splits=k_folds, shuffle=True, random_state=0)
            fold = self.args["fold"]
            fold, (train_ids, test_ids) = list(
                enumerate(kfold.split(dataset)))[fold]

            train_dataset = torch.utils.data.Subset(dataset, train_ids)
            test_dataset = torch.utils.data.Subset(dataset, test_ids)

        elif self.mode == "unbalanced-folds-intersection":
            possible_classes = [[1, 2, 3], [3, 4, 5], [5, 6, 7], [7, 8, 1]]
            classes = random.choice(possible_classes)
            self.classes = classes
            idx = (train_dataset.targets == classes[0]) | (
                train_dataset.targets == classes[1])
            train_dataset.targets = train_dataset.targets[idx]
            train_dataset.data = train_dataset.data[idx]
            # print(np.unique(train_dataset.targets))
            # print(train_dataset)
            idx = (test_dataset.targets == classes[0]) | (
                test_dataset.targets == classes[1])
            test_dataset.targets = test_dataset.targets[idx]
            test_dataset.data = test_dataset.data[idx]
            # print(np.unique(test_dataset.targets))
            # print(test_dataset)

            k_folds = 4
            dataset = ConcatDataset([train_dataset, test_dataset])
            kfold = KFold(n_splits=k_folds, shuffle=True, random_state=0)
            fold = self.args["fold"]
            fold, (train_ids, test_ids) = list(
                enumerate(kfold.split(dataset)))[fold]

            train_dataset = torch.utils.data.Subset(dataset, train_ids)
            test_dataset = torch.utils.data.Subset(dataset, test_ids)

        dataloader_train = self.sample_random_dataloader(
            train_dataset, self.num_samples, 32)
        dataloader_test = self.sample_random_dataloader(
            test_dataset, self.num_tests, 128)

        return dataloader_train, dataloader_test

    def train_model(self):
        train_loader = self.dataloader_train
        num_epochs = self.epochs
        model = self.model
        cost = self.cost
        optimizer = optim.SGD(model.parameters(), lr=self.learning_rate)
        total_step = len(train_loader)
        if self.fedsketch:
            self.old_weights = get_params(self.model)
        # print(total_step)
        for epoch in range(num_epochs):
            for i, (images, labels) in enumerate(train_loader):
                images = images.to(self.device)
                labels = labels.to(self.device)

                # Forward pass
                outputs = model(images)

                loss = cost(outputs, labels)
                # actv_last.append(outputs.detach().clone().flatten())
                # Backward and optimize
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

                if (i+1) % (total_step/num_epochs) == 0:
                    print('Epoch [{}/{}], Step [{}/{}], Loss: {:.4f}'
                          .format(epoch+1, num_epochs, i+1, total_step, loss.item()))
        if self.fedsketch:
            self.weights = get_params(self.model)
            delta = delta_weights(self.weights, self.old_weights)
            self.sketch = compress(delta, self.compression, self.length,
                                   self.desired_episilon, self.percentile, self.index_hash_function)

            # differential_garantee_pytorch(delta,self.sketch,self.desired_episilon,self.percentile)
            self.sketch_list = [i.tolist() if type(
                i) != list else i for i in self.sketch]
        # return model, loss.item()

    def eval_model(self):
        model = self.model
        test_loader = self.dataloader_test
        actv_last = []
        with torch.no_grad():
            correct = 0
            total = 0
            for images, labels in test_loader:

                images = images.to(self.device)
                labels = labels.to(self.device)
                outputs = model(images)
                actv_last.append(outputs.detach().clone().flatten())
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()

            print('Accuracy of the network on the 10000 test images: {} %'.format(
                100 * correct / total))
            return correct / total

    def get_training_args(self):
        model = self.model
        test_loader = self.dataloader_test
        actv_last = []
        with torch.no_grad():
            correct = 0
            total = 0
            for images, labels in test_loader:
                images = images.to(self.device)
                labels = labels.to(self.device)
                outputs = model(images)
                actv_last.append(outputs.detach().clone().flatten())
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()

            concat_actv = np.array(torch.cat(actv_last, axis=0))
            concat_actv -= np.mean(concat_actv)

            if self.args['encrypted']:
                XTX = self.encrypt_value(
                    1/np.sqrt((concat_actv.T.dot(concat_actv)**2).sum()))
                concat_actv_T = self.encrypt_array(concat_actv.T)
                concat_actv = self.encrypt_array(concat_actv)
                actv = [concat_actv, concat_actv_T,
                        XTX, self.cluster, self.args['encrypted']]
                return actv
            else:
                XTX = 1/np.sqrt((concat_actv.T.dot(concat_actv)**2).sum())
                concat_actv_T = concat_actv.T
                actv = [concat_actv, concat_actv_T,
                        XTX, self.cluster, self.args['encrypted']]
                return actv

    def all_metrics(self):
        acc = self.eval_model()
        return dict(zip(self.metric_names, [acc]))

    def get_weights(self):
        # print("Pesos Enviados",file=sys.stderr)
        # print(list(get_params(self.model).values()),file=sys.stderr)
        if self.fedsketch:
            weights = self.sketch_list
        else:
            weights = list(get_params(self.model).values())
        return weights

    def update_weights(self, weights):
        if self.fedsketch:
            sketch_global = [np.asarray(i) for i in weights]
            self.n_weights = decompress(self.weights, sketch_global, len(
                sketch_global), -100000, 100000, self.index_hash_function)
            for k, v in self.n_weights.items():

                self.n_weights[k] = v + self.old_weights[k]

            set_params_fedsketch(self.model, self.n_weights)
            self.model = self.model.float()
        else:
            w = [torch.from_numpy(x) for x in weights]
            set_params_fedsketch(self.model, dict(zip(self.model_keys, w)))
        # print("Pesos Atualizados",file=sys.stderr)
        # print(list(get_params(self.model).values()),file=sys.stderr)

    def agg_response_extra_info(self, agg_response):
        if self.args['encrypted']:
            agg_response["distances"] = recuperar_matriz_binaria(
                'data_temp/data.bin', self.HE_f)
        data_matrix = []

        name_dict = {}
        pos_dict = {}
        for idx, i in enumerate(agg_response["distances"]):
            name_dict[idx] = i
            pos_dict[i] = idx
            line = []
            for j in agg_response["distances"][i]:
                if self.args['encrypted']:
                    line.append(self.decrypt_value(
                        agg_response["distances"][i][j])[0])
                else:
                    line.append(agg_response["distances"][i][j])
            data_matrix.append(line)
        data_matrix = np.array(data_matrix) - 1
        data_matrix = abs(data_matrix)

        # print(data_matrix)
        # print(data_matrix.shape)
        model = AgglomerativeClustering(
            metric='precomputed', n_clusters=self.args['n_clusters'], linkage='complete').fit(data_matrix)
#
        self.cluster.clear()
        my_cluster_num = model.labels_[pos_dict[self.id_name]]
        for idx, cluster_num in enumerate(model.labels_):
            if cluster_num == my_cluster_num:
                self.cluster.append(name_dict[idx])
        # print("Cluster", file=sys.stderr)
        # print(self.cluster, file=sys.stderr)
        # print("Classes")
        # print(self.classes, file=sys.stderr)

    # def agg_response_extra_info(self, agg_response):   # versão com múltiplos valores por linha
    #     data_matrix = []

    #     name_dict = {}
    #     pos_dict = {}
    #     for idx ,i in enumerate(agg_response["distances"]):
    #         name_dict[idx] = i
    #         pos_dict[i] = idx
    #         line = []
    #         if args['encrypted']:
    #             c_res = PyCtxt(pyfhel=self.HE_f, bytestring=agg_response["distances"][i].encode('cp437'))
    #             unnorded_line = self.decrypt_value(c_res)
    #             for i in agg_response["distances"]["index"]:
    #                 line.append(unnorded_line[agg_response["distances"]["index"][i]])
    #                 print(unnorded_line)
    #                 print(line)
    #         else:
    #             for j in agg_response["distances"][i]:
    #                 line.append(agg_response["distances"][i][j])
    #         data_matrix.append(line)

    #     data_matrix = np.array(data_matrix) - 1
    #     data_matrix = abs(data_matrix)
    #     print(data_matrix)
    #     print(data_matrix.shape)
    #     model = AgglomerativeClustering(
    #         metric='precomputed', n_clusters=args['n_clusters'], linkage='complete').fit(data_matrix)

    #     self.cluster.clear()
    #     my_cluster_num = model.labels_[pos_dict[self.id_name]]
    #     for idx, cluster_num in enumerate(model.labels_):
    #         if cluster_num == my_cluster_num:
    #             self.cluster.append(name_dict[idx])

    def set_stop_true(self):
        self.stop_flag = True

    def get_stop_flag(self):
        return self.stop_flag


if __name__ == '__main__':
    trainer = TrainerCkksfed()

    for i in range(50):
        if trainer.eval_model() > 0.97:
            break
        trainer.train_model()
