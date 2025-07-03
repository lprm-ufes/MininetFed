
# FedSecPer: Similar ao DEEV, mas não conta com decaimento
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