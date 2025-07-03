import numpy as np
import pandas as pd
from tensorflow.keras.optimizers import SGD
from tensorflow.keras import layers, models
import tensorflow as tf
import os
import pickle

from .trainer_utils import read_energy

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

DATASET_PATH = 'flw/data/cifar-10-batches-py'


class TrainerCifarMod:
    def __init__(self, id, name, args) -> None:
        # id and model
        self.id = id
        self.name = name
        self.__dict__.update(args)
        self.model = self.define_model()

        # Remover cálculo aleatório de num_samples
        # self.num_samples = int(np.random.choice(np.arange(10000, 20000, 1000)))
        self.num_samples = None  # Será definido após split_data
        self.x_train, self.y_train, self.x_test, self.y_test = self.split_data()
        self.stop_flag = False
        self.args = None

    def set_args(self, args):
        self.args = args

    def get_id(self):
        return self.id

    def get_num_samples(self):
        return self.num_samples

    def define_model(self, input_shape=(32, 32, 3), n_classes=10):
        # Modelo: 3 conv layers (32, 64, 128 filtros), seguido de 4 dense (1000), tudo ReLU exceto saída Softmax
        model = models.Sequential([
            layers.Conv2D(32, kernel_size=(3, 3), activation='relu',
                          padding='same', input_shape=input_shape),
            layers.Conv2D(64, kernel_size=(3, 3),
                          activation='relu', padding='same'),
            layers.Conv2D(128, kernel_size=(3, 3),
                          activation='relu', padding='same'),
            layers.Flatten(),
            layers.Dense(1000, activation='relu'),
            layers.Dense(1000, activation='relu'),
            layers.Dense(1000, activation='relu'),
            layers.Dense(1000, activation='relu'),
            layers.Dense(n_classes, activation='softmax')
        ])

        optimizer = SGD(learning_rate=0.01)
        model.compile(optimizer=optimizer,
                      loss='categorical_crossentropy',
                      metrics=['accuracy'])
        return model

    def load_data(self):
        cifar10_dir = DATASET_PATH

        # Verifica se o diretório existe
        if not os.path.exists(cifar10_dir):
            raise FileNotFoundError(
                f"O diretório {cifar10_dir} não foi encontrado.")

        def load_batch(file):
            with open(file, 'rb') as f:
                batch = pickle.load(f, encoding='bytes')
                data = batch[b'data']
                labels = batch[b'labels']
                data = data.reshape(len(data), 3, 32, 32).transpose(0, 2, 3, 1)
                return data, labels

        # Carrega os dados de treinamento
        train_data = []
        train_labels = []
        for i in range(1, 6):
            file = os.path.join(cifar10_dir, f"data_batch_{i}")
            data, labels = load_batch(file)
            train_data.append(data)
            train_labels.extend(labels)

        train_data = np.concatenate(train_data)
        train_labels = np.array(train_labels)

        # Carrega os dados de teste
        test_file = os.path.join(cifar10_dir, "test_batch")
        test_data, test_labels = load_batch(test_file)

        test_labels = np.array(test_labels)

        return (train_data, train_labels), (test_data, test_labels)

    def split_data(self):
        (train_images, train_labels), (test_images, test_labels) = self.load_data()

        # Converting the pixels data to float type
        train_images = train_images.astype('float32')
        test_images = test_images.astype('float32')

        # Standardizing (255 is the total number of pixels an image can have)
        train_images = train_images / 255.0
        test_images = test_images / 255.0

        # One hot encoding the target class (labels)
        num_classes = 10
        train_labels_oh = tf.one_hot(np.squeeze(
            train_labels), depth=num_classes).numpy()
        test_labels_oh = tf.one_hot(np.squeeze(
            test_labels), depth=num_classes).numpy()

        # Dirichlet distribution for train set considerando self.n_clients
        alpha = 0.1
        n_clients = self.n_clients
        client_id = self.id

        idxs = np.arange(len(train_labels))
        class_idxs = [np.where(train_labels == i)[0]
                      for i in range(num_classes)]

        # Para cada classe, distribui os índices entre os clientes via Dirichlet
        client_indices = [[] for _ in range(n_clients)]
        for c, idxs_c in enumerate(class_idxs):
            if len(idxs_c) == 0:
                continue
            np.random.seed(self.seed)  # Seed para Dirichlet
            proportions = np.random.dirichlet([alpha] * n_clients)
            # Corrige para garantir soma == total de amostras da classe
            proportions = (proportions * len(idxs_c)).astype(int)
            # Ajusta para garantir soma exata
            diff = len(idxs_c) - np.sum(proportions)
            for i in range(abs(diff)):
                proportions[i % n_clients] += np.sign(diff)
            np.random.shuffle(idxs_c)
            start = 0
            for i, count in enumerate(proportions):
                client_indices[i].extend(idxs_c[start:start+count])
                start += count

        selected_train_indices = np.array(client_indices[client_id])
        np.random.shuffle(selected_train_indices)

        selected_test_indices = np.arange(len(test_labels))

        train_images = train_images[selected_train_indices]
        train_labels_oh = train_labels_oh[selected_train_indices]
        test_images = test_images[selected_test_indices]
        test_labels_oh = test_labels_oh[selected_test_indices]

        # Define num_samples corretamente
        self.num_samples = len(selected_train_indices)

        return train_images, train_labels_oh, test_images, test_labels_oh

    def train_model(self):
        self.model.fit(x=self.x_train, y=self.y_train,
                       batch_size=64, epochs=10, verbose=3)

    def eval_model(self):
        acc = self.model.evaluate(
            x=self.x_test, y=self.y_test, verbose=False)[1]
        return acc

    def all_metrics(self):
        metrics_names = self.model.metrics_names
        values = self.model.evaluate(
            x=self.x_test, y=self.y_test, verbose=False)

        dic = dict(zip(metrics_names, values))
        dic['energy_consumption'] = read_energy()
        return dic

    def get_weights(self):
        return self.model.get_weights()

    def update_weights(self, weights):
        self.model.set_weights(weights)

    def set_stop_true(self):
        self.stop_flag = True

    def get_stop_flag(self):
        return self.stop_flag


if __name__ == '__main__':
    pass
