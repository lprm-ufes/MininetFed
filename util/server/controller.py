import random
import numpy as np
import pandas as pd
from clientSelection import *
from aggregator import *
import importlib


def criar_objeto(pacote, nome_classe):
    try:
        modulo = importlib.import_module(f"{pacote}")
        classe = getattr(modulo, nome_classe)  # Obtém a classe do módulo
        return classe()  # Instancia a classe
    except (ModuleNotFoundError, AttributeError) as e:
        print(f"Erro: {e}")
        return None


class Controller:
    def __init__(self, min_trainers=2, num_rounds=5, client_selector='Random', aggregator="FedAvg"):
        self.trainer_list = []
        self.min_trainers = min_trainers
        # self.trainers_per_round = trainers_per_round
        self.current_round = 0
        self.num_rounds = num_rounds  # total number of rounds
        self.num_responses = 0  # number of responses received on aggWeights and metrics
        self.client_training_response = {}  # save weights and other info for aggregation
        self.trainer_samples = []  # save num_samples scale for agg
        self.acc_list = []
        self.mean_acc_per_round = []
        # client_selectors[client_selector]()
        self.clientSelection = criar_objeto("clientSelection", client_selector)
        self.aggregator = criar_objeto("aggregator", aggregator)
        self.metrics = {}

    # getters
    def get_trainer_list(self):
        return self.trainer_list

    def get_current_round(self):
        return self.current_round

    def get_num_trainers(self):
        return len(self.trainer_list)

    def get_num_responses(self):
        return self.num_responses

    def get_mean_acc(self):
        mean = float(np.mean(np.array(self.acc_list)))
        self.mean_acc_per_round.append(mean)  # save mean acc
        return mean

    # "setters"
    def update_metrics(self, trainer_id, metrics):
        self.metrics[trainer_id] = metrics

    def update_num_responses(self):
        self.num_responses += 1

    def reset_num_responses(self):
        self.num_responses = 0

    def reset_acc_list(self):
        self.acc_list = []

    def update_current_round(self):
        self.current_round += 1

    def add_trainer(self, trainer_id):
        self.trainer_list.append(trainer_id)

    def add_client_training_response(self, id, response):
        self.client_training_response[id] = response

    def add_accuracy(self, acc):
        self.acc_list.append(acc)

    # operations

    def select_trainers_for_round(self):
        return self.clientSelection.select_trainers_for_round(self.trainer_list, self.metrics)

    def agg_weights(self) -> dict:
        # Aggregate the models recived from clients
        agg_response = {}
        try:
            agg_response = self.aggregator.aggregate(
                self.client_training_response, self.trainer_list)
        # old aggregator standard
        except:
            agg_response = self.aggregator.aggregate(
                self.client_training_response)
        agg_response_dict = {}

        # The aggregator can return a list of weights or a dictionary mapping the id of each clients to their weights
        # The numpy arrays need to be converted to lists before return to be able to turn into json
        if isinstance(agg_response, dict):
            for r in self.trainer_list:
                try:
                    # Tem que mandar para todos os trainers, mesmo os que não treinaram
                    agg_response[r]["weights"] = [w.tolist()
                                                  for w in agg_response[r]["weights"]]
                except:
                    raise Exception(
                        f"Error: O agregador não retornou os weights do trainer {r}!")
            agg_response_dict = agg_response
        else:
            # for r in self.client_training_response:
            for r in self.trainer_list:
                client_dict = {}
                client_dict["weights"] = [w.tolist() for w in agg_response]
                agg_response_dict[r] = client_dict

        # reset weights and samples for next round
        self.client_training_response.clear()

        # agg_response_dict -> {client_id: {"weights": [], ...}}
        return agg_response_dict
