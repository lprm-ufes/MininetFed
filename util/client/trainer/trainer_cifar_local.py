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


class TrainerCifar:
    def __init__(self, id, mode) -> None:
        # id and model
        self.id = id
        self.mode = mode  # 'class' 'random' 'all'
        self.model = self.define_model()
        # split data
        # select a random number ranging from 10000 < num_samples < 20000
        self.num_samples = int(np.random.choice(np.arange(10000, 20000, 1000)))
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
        # Modelo LeNet-5
        model = models.Sequential([
            layers.Conv2D(6, kernel_size=(5, 5), activation='tanh',
                          padding='same', input_shape=(32, 32, 3)),
            layers.AveragePooling2D(pool_size=(2, 2)),
            layers.Conv2D(16, kernel_size=(5, 5), activation='tanh'),
            layers.AveragePooling2D(pool_size=(2, 2)),
            layers.Flatten(),
            layers.Dense(120, activation='tanh'),
            layers.Dense(84, activation='tanh'),
            layers.Dense(10, activation='softmax')
        ])

        # Definir o otimizador com learning rate customizado
        optimizer = SGD(learning_rate=0.01)

        # Compilar o modelo com o otimizador ajustado
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
        (train_images, train_labels), (test_images,
                                       test_labels) = self.load_data()

        # Converting the pixels data to float type
        train_images = train_images.astype('float32')
        test_images = test_images.astype('float32')

        # Standardizing (255 is the total number of pixels an image can have)
        train_images = train_images / 255.0
        test_images = test_images / 255.0

        # One hot encoding the target class (labels)
        num_classes = 10
        train_labels = tf.one_hot(np.squeeze(
            train_labels), depth=num_classes).numpy()
        test_labels = tf.one_hot(np.squeeze(
            test_labels), depth=num_classes).numpy()

        if self.mode == 'random':
            # Calculate the proportion of test samples
            test_ratio = test_images.shape[0] / \
                (train_images.shape[0] + test_images.shape[0])
            test_sample_size = int(self.num_samples * test_ratio)

            # Select random samples from train and test sets
            train_indices = np.random.choice(
                train_images.shape[0], self.num_samples - test_sample_size, replace=False)
            test_indices = np.random.choice(
                test_images.shape[0], test_sample_size, replace=False)

            train_images = train_images[train_indices]
            train_labels = train_labels[train_indices]
            test_images = test_images[test_indices]
            test_labels = test_labels[test_indices]
        elif self.mode == 'class':
            selected_label = self.id % num_classes
            train_indices = np.where(
                np.argmax(train_labels, axis=1) == selected_label)[0]
            test_indices = np.where(
                np.argmax(test_labels, axis=1) == selected_label)[0]

            train_images, train_labels = train_images[train_indices], train_labels[train_indices]
            test_images, test_labels = test_images[test_indices], test_labels[test_indices]
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
