import os
import sys

from pathlib import Path
from time import sleep
from mininet.log import info, setLogLevel
from federated.net import MininetFed
from federated.node import Server, Client

current_dir = os.path.dirname(os.path.abspath(__file__))
volume = "/flw"
volumes = [f"{Path.cwd()}:" + volume, "/tmp/.X11-unix:/tmp/.X11-unix:rw",
           "{}/client:/client".format(current_dir), "{}/server:/server".format(current_dir)]
experiment_config = {
    "ipBase": "10.0.0.0/24",
    "experiments_folder": "experiments",
    "experiment_name": "basic",
    "date_prefix": False
}
# See server/client_selection.py for the available client_selector models
server_args = {"min_trainers": 8, "num_rounds": 1, "stop_acc": 0.999,
               'client_selector': 'All', 'aggregator': "FedAvg"}
client_args = {"mode": 'random same_samples', 'num_samples': 15000,
               "trainer_class": "TrainerMNIST"}


def topology():
    net = MininetFed(**experiment_config, controller=[], broker_mode="internal",
                     default_volumes=volumes, topology_file=sys.argv[0])

    info('*** Adding Nodes...\n')
    s1 = net.addSwitch("s1", failMode='standalone')
    srv1 = net.addHost('srv1', cls=Server, script="server/server.py",
                       args=server_args, volumes=volumes,
                       dimage='mininetfed:server')
    clients = []
    for i in range(8):
        clients.append(net.addHost(f'sta{i}', cls=Client, script="client/client.py",
                                   args=client_args, volumes=volumes,
                                   dimage='mininetfed:client', numeric_id=i))

    info('*** Connecting to the MininetFed Devices...\n')
    net.connectMininetFedDevices()

    info('*** Creating links...\n')
    net.addLink(srv1, s1)
    for client in clients:
        net.addLink(client, s1)

    info('*** Starting network...\n')
    net.build()
    net.addNAT(name='nat0', linkTo='s1', ip='192.168.210.254').configDefault()
    s1.start([])

    info('*** Running FL internal devices...\n')
    net.runFlDevices()

    srv1.run(broker_addr=net.broker_addr,
             experiment_controller=net.experiment_controller)

    sleep(3)
    for client in clients:
        client.run(broker_addr=net.broker_addr,
                   experiment_controller=net.experiment_controller)

    info('*** Running Autostop...\n')
    net.wait_experiment(start_cli=False)

    info('*** Stopping network...\n')
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    topology()
