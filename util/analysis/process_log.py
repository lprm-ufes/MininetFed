import re
import pandas as pd
import csv
from datetime import datetime, timedelta
import sys
import numpy as np
import json


def extract_json(log_line):
    match = re.search(r'{.*}', log_line)
    if match:
        json_content = match.group()
        # Parse the JSON content
        return json.loads(json_content)
    else:
        raise Exception(f"No JSON found in the log line. {log_line}")


class File:
    def __init__(self, name):
        self.clients = {}
        self.name = name
        # columns=['round', 'deltaT', 'mean_accuracy']
        self.data = pd.DataFrame()
        self.net = pd.DataFrame()

        with open(self.name + '.log', 'r') as file:
            self.content = file.readlines()

        # with open(self.name + '.net', 'r') as file:
        #     self.network = file.readlines()
        self.processContent()
        # self.processNetworkContent()

    def processNetworkContent(self):
        self.n_net_saves = 0
        self.recived = 0
        self.sent = 0
        self.start_time = datetime.now()
        self.time = datetime.now()

        if len(self.network) == 0:
            raise Exception("Invalid Network log: %s.net" % self.name)

        for line in self.network:
            if 'METRIC' in line:
                if 'start' in line:
                    self.start_time = datetime.strptime(
                        line.split(' - ')[0], '%Y-%m-%d %H:%M:%S,%f')

                if 'recived' in line:
                    self.recived_old = self.recived
                    self.recived = int(
                        re.search('recived: (\d+)', line).group(1))
                    self.time = datetime.strptime(
                        line.split(' - ')[0], '%Y-%m-%d %H:%M:%S,%f')
                if 'sent' in line:
                    self.sent_old = self.sent
                    self.sent = int(re.search('sent: (\d+)', line).group(1))
                    self.time = datetime.strptime(
                        line.split(' - ')[0], '%Y-%m-%d %H:%M:%S,%f')
                    self.save_network()
            elif 'INFO' not in line:
                if 'recived' in line:
                    self.recived_old = self.recived
                    self.recived = int(
                        re.search('recived: (\d+)', line).group(1))
                    self.time = self.time + timedelta(seconds=5)
                if 'sent' in line:
                    self.sent_old = self.sent
                    self.sent = int(re.search('sent: (\d+)', line).group(1))
                    self.time = self.time + timedelta(seconds=5)
                    self.save_network()

    def save_network(self):
        self.n_net_saves = (self.time - self.start_time).total_seconds()
        new_net = pd.DataFrame({'segs': [self.n_net_saves], 'recived': [self.recived], 'sent': [
                               self.sent], 'recived_dt': [self.recived - self.recived_old], 'sent_dt': [self.sent - self.sent_old]})
        if self.net.empty:
            self.net = new_net
        else:
            self.net = pd.concat([self.net, new_net], ignore_index=True)
        # self.n_net_saves += 5 # COLOCAR TIME STAMP NO ARQUIVO .net

    def processContent(self):
        round_start_time = None
        round_end_time = None
        mean_accuracy = -1

        if 'stop_condition' not in self.content[len(self.content) - 1]:
            raise Exception("Invalid log: %s.log" % self.name)

        for line in self.content:
            if 'METRIC' in line:
                if 'round:' in line:
                    round_number = int(
                        re.search('round: (\d+)', line).group(1))

                    if round_start_time is not None:
                        round_end_time = datetime.strptime(
                            line.split(' - ')[0], '%Y-%m-%d %H:%M:%S,%f')
                        deltaT = round_end_time - round_start_time
                        self.save_data(
                            round_number - 1, deltaT.total_seconds()*1000, mean_accuracy)

                    round_start_time = datetime.strptime(
                        line.split(' - ')[0], '%Y-%m-%d %H:%M:%S,%f')

                elif 'mean_accuracy:' in line:
                    mean_accuracy = float(
                        re.search('mean_accuracy: (\d+\.\d+)', line).group(1))

                elif 'n_selected:' in line:
                    self.n_selected = int(
                        re.search('n_selected: (\d+)', line).group(1))

                elif 'selected_trainers' in line:
                    try:
                        info = extract_json(line)
                    except:
                        pass
                elif 'client_name' in line:
                    try:
                        info = extract_json(line)
                        self.clients[info['client_name']] = info
                    except:
                        pass

                elif 'stop_condition' in line and round_start_time is not None:
                    round_end_time = datetime.strptime(
                        line.split(' - ')[0], '%Y-%m-%d %H:%M:%S,%f')
                    deltaT = round_end_time - round_start_time
                    self.save_data(
                        round_number, deltaT.total_seconds()*1000,  mean_accuracy)
                    # self.save_to_csv()

    def save_data(self, round, deltaT, mean_accuracy):
        infos = {'round': [round], 'deltaT': [deltaT], 'mean_accuracy': [
            mean_accuracy], 'n_selected': [self.n_selected]}

        for client in self.clients:
            for metric in self.clients[client]:
                infos.update(
                    {f'{client}_{metric}': self.clients[client][metric]})

        new_data = pd.DataFrame(infos)
        if self.data.empty:
            self.data = new_data
        else:
            self.data = pd.concat([self.data, new_data], ignore_index=True)

    def save_to_csv(self):
        self.data.to_csv(self.name + '.csv', index=False)
        self.net.to_csv(self.name + '_net.csv', index=False)

    def get_dataframe(self):
        return self.data

    def get_net_dataframe(self):
        return self.net
