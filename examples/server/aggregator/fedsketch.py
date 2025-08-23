import numpy as np
from functools import reduce

class FedSketchAgg:
      
    def __init__(self):
      pass
    
    def aggregate(self, client_training_response):
        """Compute weighted average."""
        all_trainer_samples = []
        all_weights = []
        for client_id in client_training_response:
            all_trainer_samples.append(client_training_response[client_id]["num_samples"])
            all_weights.append(client_training_response[client_id]["weights"])
        
        num_clients = len(all_trainer_samples)
        print(num_clients)

        # Compute average weights of each layer
        weights_prime = [
            reduce(np.add, layer_updates) / num_clients
            for layer_updates in zip(*all_weights)
        ]
        return weights_prime