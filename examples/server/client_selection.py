import random


# (DEEV): Selects k clients with accuracy below the average,
# where k decreases by a decay factor at each round
class Deev:
    def __init__(self):
        self.round = 1
        self.decay = 0.01

    def select_trainers_for_round(self, trainer_list, metrics):
        mean_acc = 0
        for trainer in trainer_list:
            mean_acc += metrics[trainer]["accuracy"]
        mean_acc /= len(trainer_list)

        s = []
        for trainer in trainer_list:
            if metrics[trainer]["accuracy"] <= mean_acc:
                s.append(trainer)

        c = int(len(s) * (1 - self.decay) ** self.round)
        self.round += 1

        # Sorts the list 's' based on the trainers' accuracy
        if len(s) >= 2:
            s = sorted(s, key=lambda trainer: metrics[trainer]["accuracy"])

        if len(s) == 1 or c == 0:
            return s[:1]

        if len(s) <= c:
            return s
        else:
            # Returns the 'c' trainers with the lowest accuracy
            return s[:c]


# FedSecPer: Similar to DEEV, but without decay.
class FedSecPer:    
    def __init__(self):
      pass
    
    def select_trainers_for_round(self, trainer_list, metrics):          
        mean_acc = 0
        for trainer in trainer_list:
            mean_acc += metrics[trainer]["accuracy"]
        mean_acc /= len(trainer_list) 
          
        s = []
        for trainer in trainer_list:
            if metrics[trainer]["accuracy"] <= mean_acc:
                s.append(trainer)
              
        return s


# LeastEnergyConsumption: Selects the clients whose energy consumption so far is below the average.
class LeastEnergyConsumption:
    def __init__(self):
        pass

    def select_trainers_for_round(self, trainer_list, metrics):
        mean_energy_consumption = 0
        for trainer in trainer_list:
            mean_energy_consumption += metrics[trainer]["energy_consumption"]
        mean_energy_consumption /= len(trainer_list)

        s = []
        for trainer in trainer_list:
            if metrics[trainer]["energy_consumption"] <= mean_energy_consumption:
                s.append(trainer)

        return s


# OnlyOne: Selects only one client
class OnlyOne:
    def __init__(self):
        pass

    def select_trainers_for_round(self, trainer_list, metrics):
        s = [trainer_list[0]]

        return s


# Random This method randomly selects a set of K clients
class Random:
    def __init__(self):
        self.trainers_per_round = 5

    def select_trainers_for_round(self, trainer_list, metrics):
        if len(trainer_list) <= self.trainers_per_round:
            return trainer_list
        else:
            return random.sample(trainer_list, self.trainers_per_round)


# This method selects all clients
class All:
    def __init__(self):
        pass

    def select_trainers_for_round(self, trainer_list, metrics):
        return trainer_list