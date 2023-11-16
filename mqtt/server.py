import paho.mqtt.client as mqtt
from controller import Controller
import json
import time
import numpy as np
import sys
import logging


# total args
n = len(sys.argv)

# check args
if (n != 7):
    logging.critical("incorrect use of server.py arguments")
    print("correct use: python server.py <broker_address> <min_clients> <clients_per_round> <num_rounds> <accuracy_threshold>. <log_file_name")
    exit()

# MOSQUITTO (CONTAINER)
# sudo service mosquitto start

# CLIENTES
# MIN_TRAINERS: Minimo de treinadores
# BROKER_ADDR: IP DO BROKEN(Server so precisa de 1)

# CONDICAO DE PARADA
# NUM_ROUDS 10
# STOP ACC -> 80% acerto
BROKER_ADDR = sys.argv[1]
MIN_TRAINERS = int(sys.argv[2])
TRAINERS_PER_ROUND = int(sys.argv[3])
NUM_ROUNDS = int(sys.argv[4])
STOP_ACC = float(sys.argv[5])
CSV_PATH = sys.argv[6]

FORMAT = "%(asctime)s - %(infotype)-6s - %(levelname)s - %(message)s"

logging.basicConfig(level=logging.INFO, filename=CSV_PATH,
                    format=FORMAT, filemode="w")
metricType = {"infotype": "METRIC"}
executionType = {"infotype": "EXECUT"}
logger = logging.getLogger(__name__)

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
    subscribe_queues = ['minifed/registerQueue',
                        'minifed/preAggQueue', 'minifed/metricsQueue']
    for s in subscribe_queues:
        client.subscribe(s)

# callback for registerQueue: add trainer to the pool of trainers


def on_message_register(client, userdata, message):
    controller.add_trainer(message.payload.decode("utf-8"))
    logger.info(
        f'trainer number {message.payload.decode("utf-8")} just joined the pool', extra=executionType)
    print(
        f'trainer number {message.payload.decode("utf-8")} just joined the pool')

# callback for preAggQueue: get weights of trainers, aggregate and send back


def on_message_agg(client, userdata, message):
    m = json.loads(message.payload.decode("utf-8"))
    weights = [np.asarray(w, dtype=np.float32) for w in m['weights']]
    num_samples = m['num_samples']
    controller.add_weight(weights)  # add weight to list of weights
    # add num samples to list of num_samples
    controller.add_num_samples(num_samples)
    controller.update_num_responses()
    logger.info(
        f'received weights from trainer {m["id"]}!', extra=executionType)
    print(f'received weights from trainer {m["id"]}!')

# callback for metricsQueue: get accuracy of every trainer and compute the mean


def create_string_from_json(data):
    # data = json.loads(json_str)
    metrics_names = data['metrics_names']
    values = data['values']

    result = ''
    for i in range(len(metrics_names)):
        result += f'{metrics_names[i]}: {values[i]}'
        if i != len(metrics_names) - 1:
            result += ' - '

    return result


def on_message_metrics(client, userdata, message):
    m = json.loads(message.payload.decode("utf-8"))
    controller.add_accuracy(m['accuracy'])
    logger.info(
        f'{m["id"]} {create_string_from_json(m["metrics"])}', extra=metricType)
    controller.update_num_responses()


# connect on queue
controller = Controller(min_trainers=MIN_TRAINERS,
                        trainers_per_round=TRAINERS_PER_ROUND, num_rounds=NUM_ROUNDS)
client = mqtt.Client('server')
client.connect(BROKER_ADDR, bind_port=1883)
client.on_connect = on_connect
client.message_callback_add('minifed/registerQueue', on_message_register)
client.message_callback_add('minifed/preAggQueue', on_message_agg)
client.message_callback_add('minifed/metricsQueue', on_message_metrics)

# start loop
client.loop_start()
logger.info('starting server...', extra=executionType)
print(color.BOLD_START + 'starting server...' + color.BOLD_END)

# wait trainers to connect
while controller.get_num_trainers() < MIN_TRAINERS:
    time.sleep(1)

# begin training
while controller.get_current_round() != NUM_ROUNDS:
    controller.update_current_round()
    logger.info(f'round: {controller.get_current_round()}', extra=metricType)
    print(color.RESET + '\n' + color.BOLD_START +
          f'starting round {controller.get_current_round()}' + color.BOLD_END)
    # select trainers for round
    trainer_list = controller.get_trainer_list()
    if not trainer_list:
        logger.critical("Client's list empty", extra=executionType)
    select_trainers = controller.select_trainers_for_round()
    for t in trainer_list:
        if t in select_trainers:
            logger.info(
                f'selected: {t}', extra=metricType)
            print(
                f'selected trainer {t} for training on round {controller.get_current_round()}')
            m = json.dumps({'id': t, 'selected': True}).replace(' ', '')
            client.publish('minifed/selectionQueue', m)
        else:
            logger.info(
                f'NOT_selected: {t}', extra=metricType)
            m = json.dumps({'id': t, 'selected': False}).replace(' ', '')
            client.publish('minifed/selectionQueue', m)

    # wait for agg responses
    while controller.get_num_responses() != TRAINERS_PER_ROUND:
        time.sleep(1)
    controller.reset_num_responses()  # reset num_responses for next round

    # aggregate and send
    agg_weights = controller.agg_weights()
    response = json.dumps({'weights': [w.tolist() for w in agg_weights]})
    client.publish('minifed/posAggQueue', response)
    logger.info(f'sent aggregated weights to trainers!', extra=executionType)
    print(f'sent aggregated weights to trainers!')

    # wait for metrics response
    while controller.get_num_responses() != controller.get_num_trainers():
        time.sleep(1)
    controller.reset_num_responses()  # reset num_responses for next round
    mean_acc = controller.get_mean_acc()
    logger.info(
        f'mean_accuracy: {mean_acc}\n', extra=metricType)
    print(color.GREEN +
          f'mean accuracy on round {controller.get_current_round()} was {mean_acc}\n' + color.RESET)

    # update stop queue or continue process
    if mean_acc >= STOP_ACC:
        logger.info('stop_condition: accuracy', extra=metricType)
        print(color.RED + f'accuracy threshold met! stopping the training!')
        m = json.dumps({'stop': True})
        client.publish('minifed/stopQueue', m)
        time.sleep(1)  # time for clients to finish
        exit()
    controller.reset_acc_list()

logger.info('stop_condition: rounds', extra=metricType)
print(color.RED + f'rounds threshold met! stopping the training!' + color.RESET)
client.publish('minifed/stopQueue', m)
# PODE DA ERRO...
# controller.save_training_metrics(CSV_PATH)
client.loop_stop()
