import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, Conv1D ,Flatten,Dense
from tensorflow.keras.optimizers import SGD
import uuid
import numpy as np
import utils as harUtil
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn import preprocessing

class TrainerHar:
    ID = 0
    def __init__(self) -> None:
        # id and model
        Trainer.ID = Trainer.ID + 1
        self.id = int(Trainer.ID)
        self.nc = self.id
        self.dividir = True
        self.idColumn = "user_name"
        self.model = self.define_model()
        self.x_train, self.y_train, self.x_test, self.y_test = self.split_data()
        self.stop_flag = False
    
    def get_id(self):
        return self.id
    def set_nc(int: clients):
        self.nc= clients
    
    def get_num_samples(self):
        return self.num_samples
    
    def define_model(self, input_shape=(28, 28, 1), n_classes=10):

            model = Sequential()
            model.add(Conv1D(64,  1))
            model.add(Activation('relu'))
            model.add(Dropout())
            model.add(Conv1D(64,  1))
            model.add(Activation('relu'))
            model.add(Dropout())
            model.add(Conv1D(64, 1))
            model.add(Activation('relu'))
            model.add(Conv1D(64, 3))
            model.add(Activation('relu'))
            model.add(Flatten())
  
            opt = keras.optimizers.RMSprop(learning_rate=0.0001, decay=1e-6)
            model.compile(loss='categorical_crossentropy',
                optimizer=opt,
                metrics=['accuracy'])
            return model
        
    def split_data(self):
        x_train, y_train, x_test, y_test = self.load_data()

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
    
    def load_data(self):
        df = pd.read_csv(os.path.abspath("mqtt/data/pml.csv"), low_memory=False)
        le = preprocessing.LabelEncoder()
        idslist = []
        parts = ["belt", "arm", "dumbbell", "forearm"]
        variables =  ["roll_{}", "pitch_{}", "yaw_{}", "total_accel_{}", 
                        "accel_{}_x", "accel_{}_y", "accel_{}_z", "gyros_{}_x",
                                                    "gyros_{}_y", "gyros_{}_z"]
        var_list = []
        coluna = list()
        for part in parts:
            for var in variables:
                coluna.append(var.format(part))
                var_list.append(list(df[var.format(part)]))

        newDf = pd.DataFrame(data=[], columns= coluna)
        for x in range(len(var_list)):
            newDf[coluna[x]] = var_list[x]
        
        le.fit(df["classe"])
        newDf["classe"] = le.transform(df["classe"])

      
        if self.dividir==True:
            newDf[self.idColumn] = df[self.idColumn]
            idslist = newDf[self.idColumn].unique()
            newDf = newDf[newDf[self.idColumn] == idslist[int(id%len(idslist))-1]].drop(columns=[self.idColumn])  
        
        x_train, x_test, y_train, y_test = train_test_split(newDf.drop(columns=["classe"]).values, newDf["classe"].values,test_size=0.20, random_state=42)
    
        if not self.dividir:
            return self.partition(x_train,y_train,self.id,self.nc), self.partition(x_test,y_test,self.id,self.nc)

        return x_train, y_train, x_test, y_test

    def partition(X: np.ndarray, y: np.ndarray, id, nc):
        if len(X[0]) == 41:
            X = X[:,:-1]
    
        return np.array_split(X, int(nc))[id], np.array_split(y, int(nc))[id]


        

# if __name__ == '__main__':
#     trainer = TrainerCifar()
#     for l in trainer.model.layers:
#         print(l.name)
#         print(l.get_weights())