import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPool2D,Flatten,Dense
from tensorflow.keras.optimizers import SGD
import uuid
import numpy as np

class TrainerFmnist:
    def __init__(self) -> None:
        # id and model
        self.id = uuid.uuid1().int
        self.model = self.define_model()
        # split data
        self.num_samples = int(np.random.choice(np.arange(10000, 20000, 1000))) # select a random number ranging from 10000 < num_samples < 20000
        self.x_train, self.y_train, self.x_test, self.y_test = self.split_data()
        self.stop_flag = False
    
    def get_id(self):
        return self.id
    
    def get_num_samples(self):
        return self.num_samples
    
    def define_model(self, input_shape=(28, 28, 1), n_classes=10):
       # Model
        model = Sequential()
        # Add convolution 2D
        model.add(Conv2D(32, kernel_size=(3, 3),
                        activation='relu',
                        kernel_initializer='he_normal',
                        input_shape=(IMG_ROWS, IMG_COLS, 1)))
        model.add(MaxPooling2D((2, 2)))
        model.add(Conv2D(64, 
                        kernel_size=(3, 3), 
                        activation='relu'))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Conv2D(128, (3, 3), activation='relu'))
        model.add(Flatten())
        model.add(Dense(128, activation='relu'))
        model.add(Dense(NUM_CLASSES, activation='softmax'))
        model.compile(loss=keras.losses.categorical_crossentropy,
              optimizer='adam',
              metrics=['accuracy'])
        return model
    
    def split_data(self):
        (x_train, y_train), (x_test, y_test) =tf.keras.datasets.fashion_mnist.load_data()
        x_train = x_train / 255
        x_test = x_test / 255
        # split data
        idx_train = np.random.choice(np.arange(len(x_train)), self.num_samples, replace=False)
        x_train = x_train[idx_train]
        y_train = tf.one_hot(y_train[idx_train].astype(np.int32), depth=10)
        
        idx_test = np.random.choice(np.arange(len(x_test)), 3000, replace=False)
        x_test = x_test[idx_test]
        y_test = tf.one_hot(y_test[idx_test].astype(np.int32), depth=10)

        return x_train, y_train, x_test, y_test

    def train_model(self):
        self.model.fit(x=self.x_train, y=self.y_train, batch_size=64, epochs=10, verbose=3)

    def eval_model(self):
        acc = self.model.evaluate(x=self.x_test, y=self.y_test, verbose=False)[1]
        return acc
    
    def get_weights(self):
        return self.model.get_weights()
    
    def update_weights(self, weights):
        self.model.set_weights(weights)
    
    def set_stop_true(self):
        self.stop_flag = True
    
    def get_stop_flag(self):
        return self.stop_flag
        

# if __name__ == '__main__':
#     trainer = TrainerCifar()
#     for l in trainer.model.layers:
#         print(l.name)
#         print(l.get_weights())