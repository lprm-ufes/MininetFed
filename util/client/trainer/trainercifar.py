import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Flatten
from tensorflow.keras.layers import Conv2D, MaxPooling2D
import tensorflow.keras.optimizers as optimizers

import pandas as pd

import numpy as np

class TrainerCifar:
    def __init__(self, id, mode) -> None:
        # id and model
        self.id = id
        self.mode = mode # 'class' 'random' 'all'
        self.model = self.define_model()
        # split data
        self.num_samples = int(np.random.choice(np.arange(10000, 20000, 1000))) # select a random number ranging from 10000 < num_samples < 20000
        self.x_train, self.y_train, self.x_test, self.y_test = self.split_data()
        self.stop_flag = False
        self.args = None
    
    def set_args(self,args):
        self.args = args
    
    def get_id(self):
        return self.id
    
    def get_num_samples(self):
        return self.num_samples
    
    
    
    def define_model(self, input_shape=(32, 32, 3), n_classes=10):
        model = Sequential()
        model.add(Conv2D(32, (3, 3), padding='same',input_shape=input_shape, activation='relu'))
        model.add(Conv2D(32, (3, 3), activation='relu'))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Dropout(0.25))
        model.add(Conv2D(64, (3, 3), padding='same', activation='relu'))
        model.add(Conv2D(64, (3, 3), activation='relu'))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Dropout(0.25))
        model.add(Flatten())
        model.add(Dense(512, activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(n_classes, activation='softmax'))

        initial_learning_rate = 0.0001
        lr_schedule = optimizers.schedules.ExponentialDecay(
            initial_learning_rate, decay_steps=100000, decay_rate=0.96, staircase=True
        )

        opt = optimizers.RMSprop(learning_rate=lr_schedule)
        model.compile(loss='categorical_crossentropy', optimizer=opt, metrics=['accuracy'])


        return model


    def split_data(self):
        (train_images, train_labels), (test_images, test_labels) = tf.keras.datasets.cifar10.load_data()

        # Converting the pixels data to float type
        train_images = train_images.astype('float32')
        test_images = test_images.astype('float32')

        # Standardizing (255 is the total number of pixels an image can have)
        train_images = train_images / 255
        test_images = test_images / 255 

        # One hot encoding the target class (labels)
        num_classes = 10
        train_labels = tf.one_hot(np.squeeze(train_labels), depth=num_classes).numpy()
        test_labels = tf.one_hot(np.squeeze(test_labels), depth=num_classes).numpy()
        
        if self.mode == 'random':
            # Calculate the proportion of test samples
            test_ratio = test_images.shape[0] / (train_images.shape[0] + test_images.shape[0])
            test_sample_size = int(self.num_samples * test_ratio)

            # Select random samples from train and test sets
            train_indices = np.random.choice(train_images.shape[0], self.num_samples - test_sample_size, replace=False)
            test_indices = np.random.choice(test_images.shape[0], test_sample_size, replace=False)

            train_images = train_images[train_indices]
            train_labels = train_labels[train_indices]
            test_images = test_images[test_indices]
            test_labels = test_labels[test_indices]
        elif self.mode == 'class':
            selected_label = self.id % num_classes
            train_indices = np.where(np.argmax(train_labels, axis=1) == selected_label)[0]
            test_indices = np.where(np.argmax(test_labels, axis=1) == selected_label)[0]

            train_images, train_labels = train_images[train_indices], train_labels[train_indices]
            test_images, test_labels = test_images[test_indices], test_labels[test_indices]
        elif self.mode == 'all':
            pass
        
        return train_images, train_labels, test_images, test_labels
    

    def train_model(self):
        self.model.fit(x=self.x_train, y=self.y_train, batch_size=64, epochs=10, verbose=3)

    def eval_model(self):
        acc = self.model.evaluate(x=self.x_test, y=self.y_test, verbose=False)[1]
        return acc
    
    def all_metrics(self):
        metrics_names = self.model.metrics_names
        values = self.model.evaluate(x=self.x_test, y=self.y_test, verbose=False)
        return dict(zip(metrics_names, values))
    
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
    print(trainer.x_train.shape,trainer.y_train.shape, trainer.x_test.shape,trainer.y_test.shape)
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
