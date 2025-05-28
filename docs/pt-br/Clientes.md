## Como implementar novos Trainers

> Observação importante:
>
> Após a atualização de qualquer função implementável pelo usuário da ferramenta, é necessário rodar o instalador novamente para que essas modificações sejam acessíveis de maneira global.
>
> ```bash
> sudo ./scripts/install.sh
> ```

Para criar um Trainer personalizado, é indicado que se use algum dos Trainers fornecidos como exemplo como base e modifique o seu modelo, dataset, e manipulações dos dados como desejar.

Para que o MiniNetFED reconheça o Trainer como um Trainer válido, devem haver pelo menos os seguintes métodos implementados na classe criada:

```python
def __init__(self, id, name, args) -> None:
    """
    Inicializa o objeto Trainer com o ID, nome e argumentos fornecidos.
    """

def set_args(self, args):
    """
    Define os argumentos para o objeto Trainer quando esses são fornecidos no arquivo de configuração config.yaml.
    """

def train_model(self):
    """
    Treina o modelo nos dados de treinamento.
    """

def get_weights(self):
    """
    Retorna os pesos do modelo. Pode ser em qualquer formato desde que esteja de acordo com a função de agregação escolhida e com a implementação da função update_weights.
    """

def get_num_samples(self):
    """
    Retorna o número de amostras nos dados de treinamento.
    """

def get_training_args(self):
    """
    (Opcional) Retorna os argumentos de treinamento específicos do Trainer.
    """

def all_metrics(self):
    """
    Avalia o modelo nos dados de teste.
    Retorna um dicionário de todas as métricas usadas pelo modelo.
    """

def update_weights(self, weights):
    """
    Atualiza os pesos do modelo com os pesos dados. Pode ser em qualquer formato desde que esteja de acordo com a função de agregação escolhida e com a implementação da função get_weights.
    """

def agg_response_extra_info(self, info):
    """
    (Opcional) Processa informações adicionais enviadas pelo servidor após a agregação.
    """

def eval_model(self):
    """
    Avalia o modelo nos dados de teste.
    Retorna a acurácia do modelo em um valor entre 0 e 1.
    """

def get_stop_flag(self):
    """
    Retorna a flag de parada do objeto Trainer.
    """
    return self.stop_flag

def set_stop_true(self):
    """
    Define a flag de parada do objeto Trainer como True.
    """
    self.stop_flag = True
```
