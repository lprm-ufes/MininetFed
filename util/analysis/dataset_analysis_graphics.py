import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

class DatasetAnalysisGraphics:
  def __init__(self, trainers, mode) -> None:
    self.trainers = trainers
    self.mode = mode

    
  def class_distribution(self, y_labels=None):
      # Contando a ocorrência de cada classe em y_train
      
      for id, trainer in self.trainers.items():
      
        classes, counts = np.unique(trainer.y_train, return_counts=True)

        plt.figure(figsize=(10, 6))
        plt.bar(classes, counts)

        if y_labels is not None:
            plt.xticks(classes, y_labels)

        plt.xlabel('Classe', fontsize=18)
        plt.ylabel('Quantidade de Casos', fontsize=18)
        plt.title(f'Quantidade de casos por Classe nos Dados de Treino (cliente {id})', fontsize=16)
        plt.tick_params(labelsize=16)

        plt.show()

        # Contando a ocorrência de cada classe em y_test
        classes, counts = np.unique(trainer.y_test, return_counts=True)

        plt.figure(figsize=(10, 6))
        plt.bar(classes, counts, color="green")

        if y_labels is not None:
            plt.xticks(classes, y_labels)

        plt.xlabel('Classe', fontsize=18)
        plt.ylabel('Quantidade de Casos', fontsize=18)
        plt.title(f'Quantidade de Itens de uma Dada Classe nos Dados de Teste (cliente {id})', fontsize=16)
        plt.tick_params(labelsize=16)

        plt.show()

  def class_distribution_all(self, y_labels=None):
    all_classes = set()
    for id, trainer in self.trainers.items():
      classes, _ = np.unique(trainer.y_train, return_counts=True)
      all_classes.update(classes) 
      
    data = np.zeros((len(self.trainers),len(all_classes)))
    all_classes = np.asarray(list(all_classes))
    
    for id, trainer in self.trainers.items():
        classes, counts = np.unique(trainer.y_train, return_counts=True)
        data[id][classes] = counts

    plt.figure(figsize=(10, 6))

    plt.xlabel('Classes', fontsize=18)
    plt.ylabel('Number of Cases', fontsize=18)
    plt.title(f'Distribution of Training Cases by Class Across All Clients (mode "{self.mode}")', fontsize=16)

    plt.boxplot(data)
    
    if y_labels is not None:
        plt.xticks(all_classes+1, y_labels)

    plt.savefig(f"images_english/{self.mode}_treino.pdf")
    # plt.show()

    classes, counts = np.unique(self.trainers[0].y_test, return_counts=True)
    data = np.zeros((len(self.trainers),len(classes)))
    
    for id, trainer in self.trainers.items():
        classes, counts = np.unique(trainer.y_test, return_counts=True)
        data[id][classes] = counts

    plt.figure(figsize=(10, 6))
        
    plt.xlabel('Classes', fontsize=18)
    plt.ylabel('Number of Cases', fontsize=18)
    plt.title(f'Distribution of Testing Cases by Class Across All Clients (mode "{self.mode}")', fontsize=16)
    plt.boxplot(data)
    if y_labels is not None:
        plt.xticks(all_classes+1, y_labels)

    # plt.show()
    plt.savefig(f"images_english/{self.mode}_teste.pdf")




  # Histograma
  def histogram(self):
      for id, trainer in self.trainers.items():
        plt.figure(figsize=(15,10))
        plt.hist(trainer.x_train, bins=30)
        plt.title('Histograma')
        plt.show()

  # Boxplot
  def boxplot(self):
      for id, trainer in self.trainers.items():
        plt.figure(figsize=(10, 6))
        plt.boxplot(trainer.x_train)
        plt.title('Boxplot')
        plt.show()

  # Matriz de correlação
  def correlation_matrix(self):
      for id, trainer in self.trainers.items():
        df = pd.DataFrame(trainer.x_train)
        corr = df.corr()
        cax = plt.matshow(corr, cmap='coolwarm')
        plt.colorbar(cax)
        plt.title('Matriz de Correlação')
        plt.show()