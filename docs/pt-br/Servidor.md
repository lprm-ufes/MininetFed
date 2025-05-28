## Como implementar novas funções de seleção de cliente

> Observação importante:
>
> Após a atualização de qualquer função implementável pelo usuário da ferramenta, é necessário rodar o instalador novamente para que essas modificações sejam acessíveis de maneira global.
>
> ```bash
> sudo ./scripts/install.sh
> ```

Para implementar uma nova função de seleção de clientes, deve-se criar um novo arquivo na pasta /clientSelection com o nome desejado. Crie então uma classe com o seguinte padrão:

```python

class NomeDaFunçãoDeSeleçãoDeClientes:
    def __init__(self):
      '''
      Definição de constantes, se desejado
      '''

    def select_trainers_for_round(self, trainer_list, metrics):
      '''
      Implementação da função
      '''
      return selected_list
```

O parâmetro recebido _trainer_list_ é a lista de todos os clientes disponíveis para serem selecionados para a próxima rodada. _metrics_ é um dicionário de dicionários gerado pelo método _all_metrics_ implementado no Trainer. Os elementos desse dicionário podem ser consultados com o _id_ dos clientes em _trainer_list_. _selected_list_ é a lista de _id_ dos Trainers selecionados.

Os exemplos fornecidos junto ao MininetFed ilustram como deve ser a implementação, podendo ser usados como base para a construção de novos.

## Como implementar novas funções de agregação

Para implementar uma nova função de agregação, deve-se criar um novo arquivo na pasta /aggregator com o nome desejado. Crie então uma classe com o seguinte padrão:

```python

class NomeDoAgregador:

    def __init__(self):
      '''
      Inicialização de constantes, se necessário
      '''

    def aggregate(self, all_trainer_samples, all_weights):
        '''
        Função de agregação
        '''

        return agg_weights
```

O parâmetro recebido _all_trainer_samples_ é um array de dicionários gerado pelo método _all_metrics_ implementado no Trainer. Os elementos desse array estão dispostos na mesma ordem em que os weights de cada cliente estão dispostos no array _all_weights_.

Os exemplos fornecidos junto ao MininetFed ilustram como deve ser a implementação, podendo ser usados como base para a construção de novos.
