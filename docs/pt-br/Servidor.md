<!-- # Server padrão -->

## Como alterar entre funções de seleção de clientes

No server fornecido junto ao MiniNetFED, umas das funcionalidades é alterar entre as funções de seleção de clientes deixadas como exemplo ou implementar novas.

As funções de seleção de clientes são todas encapsuladas em uma Classe.

Para alterar entre as funções de seleção de cliente, acesse o arquivo a seguir:

```
./server/clientSelection/__init__.py
```

Nesse arquivo, edite o nome do arquivo do qual se deseja importar a função e o nome da Classe implementada.

Exemplo:

```python
from .fed_sec_per import FedSecPer as ClientSelection
```

**Observações importantes:** Não altere o **as ClientSelection**. Ele garante que, para qualquer função escolhida, demais componentes do server reconheçam adequadamente essa função.

Note também que, da forma que foi demonstrada, novas funções implementados devem estar encapsuladas em uma Classe e contidas na pasta /server/clientSelection

## Como implementar novas funções de seleção de cliente

Para implementar uma nova função de agregação, deve-se criar uma novo arquivo na pasta /clientSelection com o nome desejado. Crie então uma classe com o seguinte padrão:

```python

class NomeDaFunçãoDeSeleçãoDeClientes:
    def __init__(self):
      '''
      Definição de cosntantes de desejar
      '''

    def select_trainers_for_round(self, trainer_list,metrics):
      '''
      Implementação da função
      '''
      return selected_list


```

O parâmetro recebido _trainer_list_ é a lista de todos os clientes disponíveis para serem selecionados para a próxima rodada. _metrics_ um dicionário de dicionários gerado pelo método _all_metrics_ implementado no Trainer. Os elementos desse dicionário podem ser consultados com o _id_ dos clientes em _trainer_list_. _selected_list_ é a lista de _id_ dos Trainers selecionados.

Os exemplos deixados junto ao MiniNetFED ilustram como deve ser a implementação, podendo ser usados como base para a construção de novos.

## Como alterar entre funções de agregação

No server fornecido junto ao MiniNetFED também é possível selecionar entre as funções de agregação deixadas como exemplo ou implementar novas.

As funções de agrgação são todas encapsuladas em uma Classe.

Para alterar entre as funções de seleção de cliente, acesse o arquivo a seguir:

```
./server/aggregator/__init__.py
```

Nesse arquivo, edite o nome do arquivo do qual se deseja importar a função e o nome da Classe implementada.

Exemplo:

```python
from .fed_avg import FedAvg as Aggregator
```

**Observações importantes:** Não altere o **as Aggregate**. Ele garante que, para qualquer função escolhida, demais componentes do server reconheçam adequadamente essa função.

Note também que, da forma que foi demonstrada, novas funções implementados devem estar encapsuladas em uma Classe e contidas na pasta /server/aggregator

## Como implementar novas funções de agregação

Para implementar uma nova função de agregação, deve-se criar uma novo arquivo na pasta /aggregator com o nome desejado. Crie então uma classe com o seguinte padrão:

```python

class NomeDoAgregador:

    def __init__(self):
      '''
      Inicialização de constantes se necessário
      '''

    def aggregate(self, all_trainer_samples, all_weights):
        '''
        Função de agregação
        '''

        return agg_weights
```

O parâmetro recebido _all_trainer_sample_ é um array de dicionários gerado pelo método _all_metrics_ implementado no Trainer. Os elementos desse array estão dispostos na mesma ordem em que os weights de cada cliente estão dispostos no array _all_weights_.

Os exemplos deixados junto ao MiniNetFED ilustram como deve ser a implementação, podendo ser usados como base para a construção de novos.
