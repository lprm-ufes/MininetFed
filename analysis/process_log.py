import re
import pandas as pd
import csv
from datetime import datetime, timedelta
import sys
import numpy as np

class File:
    def __init__(self, name):
        
        self.name = name
        self.data = pd.DataFrame() # columns=['round', 'deltaT', 'mean_accuracy']
        self.net = pd.DataFrame()
        
        with open(self.name + '.log', 'r') as file:
            self.content = file.readlines()
            
        with open(self.name + '.net', 'r') as file:
            self.network = file.readlines()
        self.processContent()
        self.processNetworkContent()
        
    def processNetworkContent(self):
        self.n_net_saves = 0
        self.recived = 0
        self.sent = 0
        self.start_time = datetime.now()
        self.time = datetime.now()
        for line in self.network:
            if 'METRIC' in line:
                if 'start' in line:
                    self.start_time = datetime.strptime(line.split(' - ')[0], '%Y-%m-%d %H:%M:%S,%f')
                    
                if 'recived' in line:
                    self.recived_old = self.recived
                    self.recived = int(re.search('recived: (\d+)', line).group(1))
                    self.time = datetime.strptime(line.split(' - ')[0], '%Y-%m-%d %H:%M:%S,%f')
                if 'sent' in line:
                    self.sent_old = self.sent
                    self.sent = int(re.search('sent: (\d+)', line).group(1))
                    self.time = datetime.strptime(line.split(' - ')[0], '%Y-%m-%d %H:%M:%S,%f')
                    self.save_network()
            elif 'INFO' not in line:
                if 'recived' in line:
                    self.recived_old = self.recived
                    self.recived = int(re.search('recived: (\d+)', line).group(1))
                    self.time = self.time + timedelta(seconds=5)
                if 'sent' in line:
                    self.sent_old = self.sent
                    self.sent = int(re.search('sent: (\d+)', line).group(1))
                    self.time = self.time + timedelta(seconds=5)
                    self.save_network()
                
    def save_network(self):
        self.n_net_saves = (self.time - self.start_time).total_seconds()
        new_net = pd.DataFrame({'segs':[self.n_net_saves],'recived': [self.recived], 'sent': [self.sent], 'recived_dt': [self.recived - self.recived_old],'sent_dt':[self.sent - self.sent_old]})
        if self.net.empty:
            self.net = new_net
        else:
            self.net = pd.concat([self.net, new_net], ignore_index=True)
        # self.n_net_saves += 5 # COLOCAR TIME STAMP NO ARQUIVO .net
                
                
    
    def processContent(self):
        round_start_time = None
        round_end_time = None
        mean_accuracy = -1
        
        for line in self.content:
            if 'METRIC' in line:
                if 'round:' in line:
                    round_number = int(re.search('round: (\d+)', line).group(1))
                    
                    if round_start_time is not None:
                        round_end_time = datetime.strptime(line.split(' - ')[0], '%Y-%m-%d %H:%M:%S,%f')
                        deltaT = round_end_time - round_start_time
                        self.save_data(round_number - 1, deltaT.total_seconds()*1000, mean_accuracy)
                        
                    round_start_time = datetime.strptime(line.split(' - ')[0], '%Y-%m-%d %H:%M:%S,%f')
                    
                elif 'mean_accuracy:' in line:
                    mean_accuracy = float(
                        re.search('mean_accuracy: (\d+\.\d+)', line).group(1))
                    
                elif 'n_selected:' in line:
                    self.n_selected = int(re.search('n_selected: (\d+)', line).group(1))
                    
                elif 'stop_condition' in line and round_start_time is not None:
                    round_end_time = datetime.strptime(line.split(' - ')[0], '%Y-%m-%d %H:%M:%S,%f')
                    deltaT = round_end_time - round_start_time
                    self.save_data(round_number,deltaT.total_seconds()*1000,  mean_accuracy)
                    # self.save_to_csv()
                        
    def save_data(self, round, deltaT, mean_accuracy):
        new_data = pd.DataFrame({'round': [round], 'deltaT': [deltaT], 'mean_accuracy': [mean_accuracy],'n_selected':[self.n_selected]})
        if self.data.empty:
            self.data = new_data
        else:
            self.data = pd.concat([self.data, new_data], ignore_index=True)

    def save_to_csv(self):
        self.data.to_csv(self.name + '.csv', index=False)
        self.net.to_csv(self.name +'_net.csv',index=False)
        
    def get_dataframe(self):
        return self.data

    def get_net_dataframe(self):
        return self.net

if __name__ == '__main__':
    # total args
    n = len(sys.argv)

    #  check args
    if (n < 2):
        print("correct use: sudo python3 process_log.py <1.log> ...")
        exit()

    files = []
    
    for fileName in sys.argv[1:]:
        file = File(fileName.split('.')[0])
        file.save_to_csv()
        files.append(file)
   


# # --------------------------------------------------
    import pandas as pd
    import matplotlib.pyplot as plt
    dfs = []
    for fileName in sys.argv[1:]:
        name = fileName.split('.')[0]
        dfs.append({'name':name ,'df':pd.read_csv(name + '.csv')})
    

    # # Gráfico 1: Delta T vs Round
    # plt.figure(figsize=(10, 6))
    # plt.plot(df['round'], df['deltaT'])
    # plt.xlabel('round')
    # plt.ylabel('Delta T')
    # plt.title('Gráfico de Delta T vs round')
    # plt.show()

    # Gráfico 2: acurácia média vs round
    plt.figure(figsize=(10, 6))
    for item in dfs:
        df = item['df']
        # for column in df.columns[2:]:  # Ignorando as colunas 'round' e 'round Delta T'
        plt.plot(df['round'], df['mean_accuracy'], label=item['name'])
    plt.xlabel('round')
    plt.ylabel('Acurácia')
    plt.title('Gráfico de Acurácia vs round')
    plt.legend()
    plt.show()
    
    # Gráfico 3: n_clientes
    plt.figure(figsize=(10, 6))
    for item in dfs:
        df = item['df']
        # for column in df.columns[2:]:  # Ignorando as colunas 'round' e 'round Delta T'
        plt.plot(df['round'], df['n_selected'], label=item['name'])
    plt.xlabel('round')
    plt.ylabel('N clientes selecionados')
    plt.title('Número de clientes selecionados por round')
    plt.legend()
    plt.show()
    
    # Gráfico 4: n_clientes relativo
    if len(dfs) > 1:
        plt.figure(figsize=(10, 6))
        ref_item = dfs[0]
        ref_df = ref_item['df']
        for item in dfs[1:]:
            df = item['df']
            plt.plot(df['round'], ref_df['n_selected'] - df['n_selected'], label=item['name'])
        
        # Adicionando uma linha pontilhada em Y=0
        plt.axhline(0, color='black', linestyle='dashed')
        
        # Definindo a escala de Y para números inteiros
        y_min = int(min(ref_df['n_selected'] - df['n_selected']))
        y_max = int(max(ref_df['n_selected'] - df['n_selected']))
        plt.yticks(np.arange(y_min, y_max+1, step=1))
        
        plt.xlabel('round')
        plt.ylabel('Diferença no Nº clientes selecionados')
        plt.title(f'Gráfico de Nº clientes selecionados relativo à "{ref_item["name"]}"')
        plt.legend()
        plt.show()