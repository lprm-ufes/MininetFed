from .sketch_utils import compress, decompress, get_params, set_params, set_params_fedsketch, differential_garantee_pytorch, delta_weights, get_random_hashfunc
from sklearn.metrics import accuracy_score
import pandas as pd
import numpy as np
import glob
import sklearn
from tsai.inference import load_learner
from tsai.all import *
from tsai.basics import *
import sys
import gc
from torchvision.datasets.mnist import MNIST
from torchvision.transforms import ToTensor
from torchvision import datasets, transforms
import torchvision
from torch.utils.data import DataLoader
from torch.nn import CrossEntropyLoss
from torch.optim import Adam
import torch.nn.functional as nnf
from torch import nn, optim
import torch
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


class TrainerFedSketch:

    def __init__(self, num_id, mode) -> None:
        self.folder = "client/data"
        self.id = num_id + 1
        self.mode = mode  # client, all
        self.dls, self.X_test, self.y_test = self.split_data()
        self.num_samples = len(self.dls)
        self.criterion = LabelSmoothingCrossEntropyFlat()
        self.num_epocs = 1
        self.global_seed = 0
        self.model = self.define_model()
        self.old_weights = get_params(self.model)
        self.weights = get_params(self.model)
        self.compression = 0.00066666666  # 75x
        self.length = 20
        self.learning_rate = 1e-3
        self.global_learning_rate = 1

        self.vector_length = sum(
            p.numel() for p in self.model.model.parameters() if p.requires_grad)
        self.metrics_names = ["accuracy"]
        self.index_hash_function = [get_random_hashfunc(_max=int(
            self.compression*self.vector_length), seed=repr(j).encode()) for j in range(self.length)]
        self.args = None
        self.stop_flag = False

    def set_args(self, args):
        self.args = args
        self.global_learning_rate = self.args['global_learning_rate']
        self.global_seed = self.args['global_seed']

    def get_num_samples(self):
        return self.num_samples

    def define_model(self):
        previous_seed = torch.initial_seed()
        torch.manual_seed(self.global_seed)
        model = TST(self.dls.vars, self.dls.c, self.dls.len, dropout=.3)
        learn = Learner(self.dls, model,
                        loss_func=self.criterion, metrics=[accuracy])
        torch.manual_seed(previous_seed)

        return learn

    def split_data(self):
        dls, X_test, y_test = self.load_data()

        return dls, X_test, y_test

    def train_model(self):
        self.old_weights = get_params(self.model)
        for k, v in self.old_weights.items():
            self.old_weights[k] = v.cpu()
        self.model.fit_one_cycle(self.num_epocs, self.learning_rate)
        self.weights = get_params(self.model)

    def eval_model(self):
        test_probas, test_targets, test_preds = self.model.get_X_preds(
            self.X_test)
        pred = np.argmax(test_probas, axis=1)
        self.acc = accuracy_score(self.y_test, pred)
        return self.acc

    def all_metrics(self):
        metrics_names = self.metrics_names
        values = [self.eval_model()]
        return dict(zip(metrics_names, values))

    def get_weights(self):
        delta = delta_weights(self.weights, self.old_weights)
        self.sketch = compress(delta, self.compression,
                               self.length, 1, 90, self.index_hash_function)
        return self.sketch

    def update_weights(self, global_sketch):
        n_weights = decompress(self.weights, global_sketch, len(
            global_sketch), -10000, 10000, self.index_hash_function)
        for k, v in n_weights.items():

            n_weights[k] = v*self.global_learning_rate + self.old_weights[k]

        set_params_fedsketch(self.model, n_weights)
        self.model.model = self.model.model.float()

    def set_stop_true(self):
        self.stop_flag = True

    def get_stop_flag(self):
        return self.stop_flag

    def load_data(self):
        class_map = {
            "dws": 0,
            "ups": 1,
            "wlk": 2,
            "std": 3,
            "sit": 4,
            "jog": 5
        }
        subject = "/sub_" + str(self.id) + ".csv"
        path = "client/data/MotionSensor/A_DeviceMotion_data/"
        paths = [x[0] for x in os.walk(path)]
        paths.remove(path)
        X = []
        y = []
        for p in paths:
            df_raw = pd.read_csv(p+subject)
            df_raw["Class"] = p.split('/')[-1].split('_')[0]
            X.append(df_raw.drop("Class", axis=1))
            y.append(df_raw["Class"])
        X = np.concatenate(X)
        y = np.concatenate(y)

        X = np.atleast_3d(X).transpose(0, 2, 1)
        labeler = ReLabeler(class_map)
        y = labeler(y)
        y.astype(int)
        splits = get_splits(y,
                            n_splits=1,
                            valid_size=0.3,
                            test_size=0.1,
                            shuffle=True,
                            balance=False,
                            stratify=True,
                            random_state=42,
                            show_plot=False,
                            verbose=True)
        tfms = [None, [Categorize()]]
        dsets = TSDatasets(X, y, tfms=tfms, splits=splits)

        bs = 256
        dls = TSDataLoaders.from_dsets(dsets.train, dsets.valid, bs=[
                                       bs, bs*2], device="cpu")
        X_test = X[splits[1]]
        y_test = y[splits[1]]
        return dls, X_test, y_test


# if __name__ == '__main__':
#    trainer = TrainerFedSketch(0,'client')
#    #x_train, y_train, x_test, y_test = trainer.load_data()
#    # print(x_train.shape,y_train.shape, x_test.shape,y_test.shape)
#    #acc = trainer.eval_model()
#    #print(acc)
#    acc = 0.0
#    while acc < 0.9:
#        trainer.train_model()
#        sketch = trainer.get_weights()
#        print(sketch.shape)
#        trainer.update_weights(sketch)
#        trainer.model.model = trainer.model.model.float()
#        acc = trainer.eval_model()
#        print("Accuracy: " + str(acc))

    # y_predict = trainer.model.predict(x_test)

    # Convertendo os arrays numpy para DataFrames
    # x_train_df = pd.DataFrame(x_train)
    # y_train_df = pd.DataFrame(y_train)
    # x_test_df = pd.DataFrame(x_test)
    # y_test_df = pd.DataFrame(y_test)
    # y_predict_df = pd.DataFrame(y_predict)

    # Salvando os DataFrames como arquivos CSV

    # x_train_df.to_csv('x_train.csv', index=False)
    # y_train_df.to_csv('y_train.csv', index=False)
    # x_test_df.to_csv('x_test.csv', index=False)
    # y_test_df.to_csv('y_test.csv', index=False)
    # y_predict_df.to_csv('y_predict.csv', index=False)
