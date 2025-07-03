import numpy as np
import pandas as pd
from tensorflow.keras.optimizers import SGD
from tensorflow.keras import layers, models
import tensorflow as tf
import os
import sys

from datetime import datetime

from .trainer_utils import read_energy, copiar_arquivo

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

DATASET_PATH = 'flw/data/MNIST'


class MNISTLoader:
    def __init__(self, data_path):
        self.data_path = data_path

    def load_data(self):
        """
        Load MNIST dataset from local files.

        Returns:
            (tuple): (train_images, train_labels), (test_images, test_labels) 
        """
        train_images_path = os.path.join(
            self.data_path, 'train-images.idx3-ubyte')
        train_labels_path = os.path.join(
            self.data_path, 'train-labels.idx1-ubyte')
        test_images_path = os.path.join(
            self.data_path, 't10k-images.idx3-ubyte')
        test_labels_path = os.path.join(
            self.data_path, 't10k-labels.idx1-ubyte')

        train_images = self._load_images(train_images_path)
        train_labels = self._load_labels(train_labels_path)
        test_images = self._load_images(test_images_path)
        test_labels = self._load_labels(test_labels_path)

        return (train_images, train_labels), (test_images, test_labels)

    def _load_images(self, file_path):
        """
        Load image data from file.

        Args:
            file_path (str): Path to the image file.

        Returns:
            numpy.ndarray: Array of images.
        """
        with open(file_path, 'rb') as f:
            _ = int.from_bytes(f.read(4), 'big')  # Magic number
            num_images = int.from_bytes(f.read(4), 'big')
            rows = int.from_bytes(f.read(4), 'big')
            cols = int.from_bytes(f.read(4), 'big')

            image_data = np.frombuffer(f.read(), dtype=np.uint8)
            images = image_data.reshape(num_images, rows, cols)

        return images / 255.0  # Normalize pixel values to [0, 1]

    def _load_labels(self, file_path):
        """
        Load label data from file.

        Args:
            file_path (str): Path to the label file.

        Returns:
            numpy.ndarray: Array of labels.
        """
        with open(file_path, 'rb') as f:
            _ = int.from_bytes(f.read(4), 'big')  # Magic number
            num_labels = int.from_bytes(f.read(4), 'big')

            label_data = np.frombuffer(f.read(), dtype=np.uint8)

        return label_data


class TrainerMNIST:
    def __init__(self, id, name, args) -> None:

        # Initiate
        self.id = id
        self.name = name
        # self.mode = mode  # 'class' 'random' 'all'
        self.__dict__.update(args)
        mode = self.mode
        # define model
        self.model = self.define_model()

        # split data
        # select a random number ranging from 10000 < num_samples < 20000
        self.num_samples = -1

        if 'r_samples' in mode:
            self.num_samples = int(np.random.choice(
                np.arange(10000, 20000, 1000)))
        elif 'same_samples' in mode:
            self.num_samples = int(args['num_samples'])

        print(
            f"mode:{mode}, n_samples:{self.num_samples}", file=sys.stderr)

        self.x_train, self.y_train, self.x_test, self.y_test = self.split_data()

        if self.num_samples == -1:
            self.num_samples == len(self.y_train)

        self.stop_flag = False
        self.args = None

    def set_args(self, args):
        self.args = args

    def get_id(self):
        return self.id

    def get_num_samples(self):
        return self.num_samples

    def define_model(self, input_shape=(28, 28, 1), n_classes=10):
        # Modelo LeNet-5 ajustado para o MNIST
        model = models.Sequential([
            layers.Conv2D(6, kernel_size=(5, 5), activation='tanh',
                          padding='same', input_shape=input_shape),
            layers.AveragePooling2D(pool_size=(2, 2)),
            layers.Conv2D(16, kernel_size=(5, 5), activation='tanh'),
            layers.AveragePooling2D(pool_size=(2, 2)),
            layers.Flatten(),
            layers.Dense(120, activation='tanh'),
            layers.Dense(84, activation='tanh'),
            layers.Dense(n_classes, activation='softmax')
        ])

        # Definir o otimizador com learning rate customizado
        optimizer = SGD(learning_rate=0.01)

        # Compilar o modelo com o otimizador ajustado
        model.compile(optimizer=optimizer,
                      loss='categorical_crossentropy',
                      metrics=['accuracy'])

        return model

    def load_data(self):
        loader = MNISTLoader(DATASET_PATH)
        return loader.load_data()

    def split_data(self):
        (train_images, train_labels), (test_images,
                                       test_labels) = self.load_data()

        # # Converting the pixels data to float type
        # train_images = train_images.astype('float32')
        # test_images = test_images.astype('float32')

        # # Standardizing (255 is the total number of pixels an image can have)
        # train_images = train_images / 255.0
        # test_images = test_images / 255.0

        # One hot encoding the target class (labels)
        num_classes = 10
        train_labels = tf.one_hot(np.squeeze(
            train_labels), depth=num_classes).numpy()
        test_labels = tf.one_hot(np.squeeze(
            test_labels), depth=num_classes).numpy()

        if 'n_classes' in self.mode:
            # Criar um gerador de números aleatórios usando self.id como seed
            rng = np.random.default_rng(seed=(self.id + 1))

            # Selecionar n_classes de maneira aleatória e determinística com base na seed
            selected_classes = rng.choice(
                num_classes, size=self.n_classes_per_trainer, replace=False)

            # Filtrar índices para as classes selecionadas
            train_indices = np.where(
                np.isin(np.argmax(train_labels, axis=1), selected_classes))[0]
            test_indices = np.where(
                np.isin(np.argmax(test_labels, axis=1), selected_classes))[0]

            # Selecionar os dados correspondentes
            train_images, train_labels = train_images[train_indices], train_labels[train_indices]
            test_images, test_labels = test_images[test_indices], test_labels[test_indices]

        if 'random' in self.mode:
            # Calculate the proportion of test samples
            test_ratio = test_images.shape[0] / \
                (train_images.shape[0] + test_images.shape[0])
            test_sample_size = int(self.num_samples * test_ratio)

            print(
                f"test_ratio:{test_ratio}, test_sample_size:{test_sample_size}, train_sample_size:{self.num_samples - test_sample_size} ", file=sys.stderr)

            # Select random samples from train and test sets
            train_indices = np.random.choice(
                train_images.shape[0], self.num_samples - test_sample_size, replace=False)
            test_indices = np.random.choice(
                test_images.shape[0], test_sample_size, replace=False)

            train_images = train_images[train_indices]
            train_labels = train_labels[train_indices]
            test_images = test_images[test_indices]
            test_labels = test_labels[test_indices]

        elif self.mode == 'all':
            pass

        return train_images, train_labels, test_images, test_labels

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
        self.now = datetime.now()
        now_str = self.now.strftime("%Hh%Mm%Ss")
        copiar_arquivo("../tmp/consumption.log",
                       f"client_log/{now_str}{self.name}.log")
        self.stop_flag = True

    def get_stop_flag(self):
        return self.stop_flag


if __name__ == '__main__':
    trainer = TrainerCifar(0, 'random')
    # x_train, y_train, x_test, y_test = trainer.load_data()
    print(trainer.x_train.shape, trainer.y_train.shape,
          trainer.x_test.shape, trainer.y_test.shape)
    acc = 0.0
    while acc < 0.9:
        trainer.train_model()
        acc = trainer.eval_model()
        print(acc)

    # y_predict = trainer.model.predict(trainer.x_test)

    # # Convertendo os arrays numpy para DataFrames
    # x_train_df = pd.DataFrame(trainer.x_train)
    # y_train_df = pd.DataFrame(trainer.y_train)
    # x_test_df = pd.DataFrame(trainer.x_test)
    # y_test_df = pd.DataFrame(trainer.y_test)
    # y_predict_df = pd.DataFrame(y_predict)

    # # Salvando os DataFrames como arquivos CSV

    # x_train_df.to_csv('x_train.csv', index=False)
    # y_train_df.to_csv('y_train.csv', index=False)
    # x_test_df.to_csv('x_test.csv', index=False)
    # y_test_df.to_csv('y_test.csv', index=False)
    # y_predict_df.to_csv('y_predict.csv', index=False)
