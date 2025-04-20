## How to implement new Trainers

To create a custom Trainer, it is recommended to use one of the provided Trainers as a base and modify its model, dataset, and data manipulations as desired.

For MiniNetFED to recognize the Trainer as a valid Trainer, the created class must implement at least the following methods:

```python
def __init__(self, id, name, args) -> None:
    """
    Initializes the Trainer object with the provided ID, name, and arguments.
    """

def set_args(self, args):
    """
    Sets the arguments for the Trainer object when they are provided in the config.yaml configuration file.
    """

def train_model(self):
    """
    Trains the model on the training data.
    """

def get_weights(self):
    """
    Returns the model's weights. These can be in any format as long as they are compatible with the chosen aggregation function and the implementation of the update_weights function.
    """

def get_num_samples(self):
    """
    Returns the number of samples in the training data.
    """

def get_training_args(self):
    """
    (Optional) Returns the training-specific arguments of the Trainer.
    """

def all_metrics(self):
    """
    Evaluates the model on the test data.
    Returns a dictionary of all metrics used by the model.
    """

def update_weights(self, weights):
    """
    Updates the model's weights with the given weights. These can be in any format as long as they are compatible with the chosen aggregation function and the implementation of the get_weights function.
    """

def agg_response_extra_info(self, info):
    """
    (Optional) Processes additional information sent by the server after aggregation.
    """

def eval_model(self):
    """
    Evaluates the model on the test data.
    Returns the model's accuracy as a value between 0 and 1.
    """

def get_stop_flag(self):
    """
    Returns the stop flag of the Trainer object.
    """
    return self.stop_flag

def set_stop_true(self):
    """
    Sets the stop flag of the Trainer object to True.
    """
    self.stop_flag = True
```
