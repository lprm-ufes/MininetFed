import paho.mqtt.client as mqtt
from trainer import Trainer
import json
import numpy as np
import time
import sys

# total args
n = len(sys.argv)

# check args
if (n != 3):
    print("correct use: python client.py <broker_address>. <name>")
    exit()

BROKER_ADDR = sys.argv[1]
NAME_NODE   = sys.argv[2]
# class for coloring messages on terminal


class color:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD_START = '\033[1m'
    BOLD_END = '\033[0m'
    RESET = "\x1B[0m"

# subscribe to queues on connection


def on_connect(client, userdata, flags, rc):
    subscribe_queues = ['minifed/selectionQueue',
                        'minifed/posAggQueue', 'minifed/stopQueue']
    for s in subscribe_queues:
        client.subscribe(s)

# callback for selectionQueue: if trainer gets chosen, then starts training, else just wait


def on_message_selection(client, userdata, message):
    msg = json.loads(message.payload.decode("utf-8"))
    if msg['id'] == trainer.get_id():
        if bool(msg['selected']) == True:
            print(color.BOLD_START + 'new round starting' + color.BOLD_END)
            print(
                f'trainer was selected for training this round and will start training!')
            trainer.train_model()
            response = json.dumps({'id': trainer.get_id(), 'weights': [w.tolist(
            ) for w in trainer.get_weights()], 'num_samples': trainer.get_num_samples()})
            client.publish('minifed/preAggQueue', response)
            print(f'finished training and sent weights!')
        else:
            print(color.BOLD_START + 'new round starting' + color.BOLD_END)
            print(f'trainer was not selected for training this round')

# callback for posAggQueue: gets aggregated weights and publish validation results on the metricsQueue


def on_message_agg(client, userdata, message):
    print(f'received aggregated weights!')
    msg = json.loads(message.payload.decode("utf-8"))
    agg_weights = [np.asarray(w, dtype=np.float32) for w in msg["weights"]]
    trainer.update_weights(agg_weights)
    response = json.dumps({'id': trainer.get_id(
    ), 'accuracy': trainer.eval_model(), "metrics": trainer.all_metrics()})
    print(f'sending eval metrics!\n')
    client.publish('minifed/metricsQueue', response)

# callback for stopQueue: if conditions are met, stop training and exit process


def on_message_stop(client, userdata, message):
    print(color.RED + f'received message to stop!')
    trainer.set_stop_true()
    exit()


# connect on queue and send register
trainer = Trainer(NAME_NODE)
client = mqtt.Client(str(trainer.get_id()))
client.connect(BROKER_ADDR, keepalive=2000)
client.on_connect = on_connect
client.message_callback_add('minifed/selectionQueue', on_message_selection)
client.message_callback_add('minifed/posAggQueue', on_message_agg)
client.message_callback_add('minifed/stopQueue', on_message_stop)
client.publish('minifed/registerQueue', trainer.get_id())
print(color.BOLD_START +
      f'trainer {trainer.get_id()} connected!\n' + color.BOLD_END)
# start waiting for jobs
client.loop_start()

while not trainer.get_stop_flag():
    time.sleep(1)

client.loop_stop()
