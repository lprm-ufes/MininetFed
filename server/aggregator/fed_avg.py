import numpy as np

class FedAvg:
      
    def __init__(self):
      pass
    
    def aggregate(self, all_trainer_samples, all_weights):
        scaling_factor = list(np.array(all_trainer_samples) / np.array(all_trainer_samples).sum())
        
        # scale weights
        for scaling, weights in zip(scaling_factor, all_weights):
            for i in range(0, len(weights)):
                weights[i] = weights[i] * scaling
        
        # agg weights
        agg_weights = []
        for layer in range(0, len(all_weights[0])):
            var = []
            for model in range(0, len(all_weights)):
                var.append(all_weights[model][layer])
            agg_weights.append(sum(var))

        return agg_weights