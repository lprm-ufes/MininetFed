## How to Implement New Client Selection Functions

> Important Note:
>
> After updating any user-implementable function in the tool, you must run the installer again for these modifications to be globally accessible.
>
> ```bash
> sudo ./scripts/install.sh
> ```

To implement a new client selection function, you must create a new file in the /clientSelection folder with the desired name. Then, create a class with the following pattern:

```python

class ClientSelectionFunctionName:
    def __init__(self):
      '''
      Definition of constants, if desired
      '''

    def select_trainers_for_round(self, trainer_list, metrics):
      '''
      Function implementation
      '''
      return selected_list
```

The parameter _trainer_list_ is the list of all clients available to be selected for the next round. _metrics_ is a dictionary of dictionaries generated by the _all_metrics_ method implemented in the Trainer. The elements of this dictionary can be accessed using the _id_ of the clients in _trainer_list_. _selected_list_ is the list of _id_ of the selected Trainers.

The examples provided with MininetFed illustrate how the implementation should be done and can be used as a basis for creating new ones.

## How to Implement New Aggregation Functions

To implement a new aggregation function, you must create a new file in the /aggregator folder with the desired name. Then, create a class with the following pattern:

```python

class AggregatorName:

    def __init__(self):
      '''
      Initialization of constants, if necessary
      '''

    def aggregate(self, all_trainer_samples, all_weights):
        '''
        Aggregation function
        '''

        return agg_weights
```

The parameter _all_trainer_samples_ is an array of dictionaries generated by the _all_metrics_ method implemented in the Trainer. The elements of this array are arranged in the same order as the weights of each client in the _all_weights_ array.

The examples provided with MininetFed illustrate how the implementation should be done and can be used as a basis for creating new ones.
