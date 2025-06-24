# Dispositivo eu escolho você (DEEV): Seleciona k clientes com acurácia menor que a média, 
# onde k decresce com um fator de descrecimento a cada rodada
class Deev:
      
    def __init__(self):
      self.round = 1
      self.decay = 0.01 # Valor usado não é comentado no artigo
    
    def select_trainers_for_round(self, trainer_list, metrics):          
        mean_acc = 0
        for trainer in trainer_list:
            mean_acc += metrics[trainer]["accuracy"]
        mean_acc /= len(trainer_list) 
          
        s = []
        for trainer in trainer_list:
            if metrics[trainer]["accuracy"] <= mean_acc:
                s.append(trainer)
        
        c = int(len(s) * (1 - self.decay)**self.round)
        self.round += 1
          
        # Ordena a lista 's' com base na acurácia dos treinadores
        if len(s) >= 2:
            s = sorted(s, key=lambda trainer: metrics[trainer]["accuracy"])

        if len(s) == 1 or c == 0:
            return s[:1]
        
        if len(s) <= c:
            return s
        else:
            # Retorna os 'c' treinadores com menor acurácia
            return s[:c]
