import yaml

class Config:
    
    def __init__(self, filename):
        with open(filename, 'r') as f:
            self.config = yaml.safe_load(f)

    def get(self, key):
        return self.config.get(key)
    
    def data(self):
      return self.config
    
    def n_clients(self):
        n = 0
        for x in self.get("client_types"):
            n += x["amount"]
        return n
    
 

# # Exemplo de uso
# config = Config('flower/config.yaml')
# print(config.data())
# server = config.get(server)
# print(server["memory"])
