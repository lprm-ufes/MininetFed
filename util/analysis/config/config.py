import yaml

class Config:
    def __init__(self, filename):
        with open(filename, 'r') as f:
            self.config = yaml.safe_load(f)

    def get(self, key):
        return self.config.get(key)
    
    def data(self):
      return self.config
