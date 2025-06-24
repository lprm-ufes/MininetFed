import paho.mqtt.client as mqtt
from controller import Controller
import json
import time
import numpy as np
import sys
import logging
import os


def default(obj):
    if type(obj).__module__ == np.__name__:
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return obj.item()
    # elif type(obj).__module__ == torch.__name__:
    #     if isinstance(obj, torch.Tensor):
    #         return obj.tolist()
    else:
        try:
            from Pyfhel import PyCtxt
            if isinstance(obj, PyCtxt):
                return obj.to_bytes().decode('cp437')
        except:
            pass
    raise TypeError('Tipo não pode ser serializado:', type(obj))


FORMAT = "%(asctime)s - %(infotype)-6s - %(levelname)s - %(message)s"


def server():
    # total args
    os.umask(0o000)
    n = len(sys.argv)

    # check args
    if (n < 4):
        logging.critical("incorrect use of server.py arguments")
        # <min_clients> <num_rounds> <accuracy_threshold>
        print("correct use: python server.py <broker_address> <arquivo.log> <args>.")
        exit()

    server_args = json.loads(sys.argv[3])

    broker_addr = sys.argv[1]
    log_file = sys.argv[2]
    min_trainers = server_args["min_trainers"]
    client_selector = server_args["client_selector"]
    aggregator = server_args["aggregator"]
    nun_rounds = server_args["num_rounds"]
    stop_acc = server_args["stop_acc"]
    client_args = server_args.get("client")

    logging.basicConfig(level=logging.INFO, filename=log_file,
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
                            'minifed/preAggQueue', 'minifed/metricsQueue', 'minifed/ready']
        for s in subscribe_queues:
            client.subscribe(s)

    # callback for registerQueue: add trainer to the pool of trainers
    def on_message_ready(client, userdata, message):
        m = json.loads(message.payload.decode("utf-8"))
        controller.add_trainer(m["id"])

    def on_message_register(client, userdata, message):
        m = json.loads(message.payload.decode("utf-8"))
        controller.update_metrics(m["id"], m['metrics'])
        logger.info(
            f'trainer number {m["id"]} just joined the pool', extra=executionType)
        print(
            f'trainer number {m["id"]} just joined the pool')

        client.publish(
            'minifed/serverArgs', json.dumps({"id": m["id"], "args": client_args}))

    # callback for preAggQueue: get weights of trainers, aggregate and send back
    def on_message_agg(client, userdata, message):
        m = json.loads(message.payload.decode("utf-8"))
        client_training_response = {}
        weights = [np.asarray(w, dtype=np.float32) for w in m['weights']]
        client_training_response["weights"] = weights

        if 'training_args' in m:
            client_training_response["training_args"] = m['training_args']

        num_samples = m['num_samples']
        client_training_response["num_samples"] = num_samples
        controller.add_client_training_response(
            m['id'], client_training_response)
        controller.update_num_responses()
        logger.info(
            f'received weights from trainer {m["id"]}!', extra=executionType)
        print(f'received weights from trainer {m["id"]}!')

    # def create_string_from_json(data):
    #     return " - ".join(f"{name}: {value}" for name, value in data.items())

    # callback for metricsQueue: get the metrics from each client after it finish its round
    def on_message_metrics(client, userdata, message):
        m = json.loads(message.payload.decode("utf-8"))
        controller.add_accuracy(m['metrics']['accuracy'])
        controller.update_metrics(m["id"], m['metrics'])
        m["metrics"]["client_name"] = m["id"]
        logger.info(
            f'{json.dumps(m["metrics"])}', extra=metricType)
        controller.update_num_responses()

    # connect on queue
    controller = Controller(min_trainers=min_trainers,
                            num_rounds=nun_rounds, client_selector=client_selector, aggregator=aggregator)
    client = mqtt.Client('server')
    client.connect(broker_addr, bind_port=1883)
    client.on_connect = on_connect
    client.message_callback_add('minifed/registerQueue', on_message_register)
    client.message_callback_add('minifed/preAggQueue', on_message_agg)
    client.message_callback_add('minifed/metricsQueue', on_message_metrics)
    client.message_callback_add('minifed/ready', on_message_ready)

    # start loop
    client.loop_start()
    logger.info('starting server...', extra=executionType)
    print(color.BOLD_START + 'starting server...' + color.BOLD_END)
    client.publish('minifed/autoWaitContinue', json.dumps({'continue': True}))

    # wait trainers to connect
    while controller.get_num_trainers() < min_trainers:
        time.sleep(1)

    # begin training
    selected_qtd = 0
    while controller.get_current_round() != nun_rounds:
        controller.update_current_round()
        logger.info(
            f'round: {controller.get_current_round()}', extra=metricType)
        print(color.RESET + '\n' + color.BOLD_START +
              f'starting round {controller.get_current_round()}' + color.BOLD_END)
        # select trainers for round
        trainer_list = controller.get_trainer_list()
        if not trainer_list:
            logger.critical("Client's list empty", extra=executionType)
        select_trainers = controller.select_trainers_for_round()
        selected_qtd = len(select_trainers)

        logger.info(f"n_selected: {len(select_trainers)}", extra=metricType)
        logger.info(
            f"{json.dumps({'selected_trainers': select_trainers})}", extra=metricType)
        for t in trainer_list:
            if t in select_trainers:
                # logger.info(
                #     f'selected: {t}', extra=metricType)
                print(
                    f'selected trainer {t} for training on round {controller.get_current_round()}')
                m = json.dumps({'id': t, 'selected': True}).replace(' ', '')
                client.publish('minifed/selectionQueue', m)
            else:
                # logger.info(
                #     f'NOT_selected: {t}', extra=metricType)
                m = json.dumps({'id': t, 'selected': False}).replace(' ', '')
                client.publish('minifed/selectionQueue', m)

        # wait for agg responses
        while controller.get_num_responses() != selected_qtd:
            time.sleep(1)
        controller.reset_num_responses()  # reset num_responses for next round

        # aggregate and send
        agg_response = controller.agg_weights()
        response = json.dumps({'agg_response': agg_response}, default=default)
        client.publish('minifed/posAggQueue', response)
        logger.info(f'sent aggregated weights to trainers!',
                    extra=executionType)
        print(f'sent aggregated weights to trainers and waiting trainers metrics!')

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
        if mean_acc >= stop_acc:
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
    client.loop_stop()


if __name__ == "__main__":
    server()
