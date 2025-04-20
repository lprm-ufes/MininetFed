<!-- # Cliente padrão -->

## Como alterar entre os trainers

No cliente fornecido junto ao MiniNetFED, uma das funcionalidades é poder escolher entre os Trainers fornecidos de exemplo ou implementar um Trainer para os seus próprios experimentos.

Para alternar entre os trainers, acesse o arquivo a seguir

```
./client/trainer/__init__.py
```

Nesse arquivo, edite o nome do arquivo do qual se deseja importar o Trainer e o nome da Classe implementada.

Exemplo:

```
from .trainerhar import TrainerHar as Trainer
```

**Observações importantes:** Não altere o **as Trainer**. Ele garante que, para qualquer Trainer escolhido, demais componentes do cliente reconheçam adequadamente o Trainer.

Note também que, da forma que foi demonstrada, novos Trainers implementados devem estar contidos na pasta /client/trainer

## Como implementar novos Trainers

Para criar um Trainer personalizado, é indicado que se use algum dos Trainers fornecidos como exemplo como base e modifique o seu modelo, dataset, e manipulações dos dados como desejar.

Para que o MiniNetFED reconheça o Trainer como um Trainer válido, devem haver pelo menos os seguintes métodos implementados na classe criada:

```python
def __init__(self, ext_id, mode) -> None:
    """
    Inicializa o objeto Trainer com o ID externo e modo de operação do Trainer.
    """

def set_args(self, args):
    """
    Define os argumentos para o objeto Trainer quando esses são fonecidos no arquivo de configuração config.yaml.
    """

def get_num_samples(self):
    """
    Retorna o número de amostras nos dados de treinamento.
    """

def split_data(self):
    """
    Carrega os dados e os divide em conjuntos de treinamento e teste.
    Retorna os dados de treinamento e teste da seguinte forma

    return x_train, y_train, x_test, y_test
    """

def train_model(self):
    """
    Treina o modelo nos dados de treinamento.
    """

def eval_model(self):
    """
    Avalia o modelo nos dados de teste.
    Retorna a acurácia do modelo em um valor entre 0 e 1.
    """

def all_metrics(self):
    """
    Avalia o modelo nos dados de teste.
    Retorna um dicionário de todas as métricas usadas pelo modelo.
    """

def get_weights(self):
    """
    Retorna os pesos do modelo. Pode ser em qualquer formato desde que esse esteja de acordo com a função de agregação escolhida e com a implementação da função update_weights
    """

def update_weights(self, weights):
    """
    Atualiza os pesos do modelo com os pesos dados. Pode ser em qualquer formato desde que esse esteja de acordo com a função de agregação escolhida e com a implementação da função get_weights.
    """

def set_stop_true(self):
    """
    Define a flag de parada do objeto TrainerHar como True.
    """
    self.stop_flag = True

def get_stop_flag(self):
    """
    Retorna a flag de parada do objeto TrainerHar.
    """
    return self.stop_flag


```
