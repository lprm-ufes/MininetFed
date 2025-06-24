import sys
from pathlib import Path
from time import sleep

from mininet.log import info, setLogLevel

from containernet.link import TCLink
from federated.net import MininetFed
from federated.node import Server, Client


volume = "/flw"
volumes = [f"{Path.cwd()}:" + volume, "/tmp/.X11-unix:/tmp/.X11-unix:rw"]

experiment_config = {
    "ipBase": "10.0.0.0/24",
    "experiments_folder": "experiments",
    "experiment_name": "limitations",
    "date_prefix": False
}

server_args = {"min_trainers": 8, "num_rounds": 1,
               "stop_acc": 0.999, 'client_selector': 'All', 'aggregator': "FedAvg"}
client_args = {"mode": 'random same_samples',
               'num_samples': 15000, "trainer_class": "TrainerMNIST"}

bw = [10, 10, 1, 10, 10, 1, None, 1]
delay = ["10ms", "10ms", "10ms", "10ms", "10ms", "10ms", None, "1ms"]
loss = [None, None, None, None, None, None, None, None]
cpu_shares = [512, 256, 1024, 1024, 1024, 1024, 1024, 1024]

client_mem_lim = ["512m", "512m", "512m",
                  "512m", "512m", "512m", "512m", "512m"]


def topology():
    net = MininetFed(
        **experiment_config,
        controller=[],
        default_volumes=volumes,
        topology_file=sys.argv[0]
    )

    info('*** Adding Nodes...\n')
    s1 = net.addSwitch("s1", failMode='standalone')

    net.configureMininetFedInternalDevices()

    srv1 = net.addHost('srv1', cls=Server, script="server/server.py",
                       args=server_args, volumes=volumes,
                       dimage='mininetfed:server',
                       env="../env"
                       )

    clients = []
    for i in range(8):
        clients.append(net.addHost(f'sta{i}', cls=Client, script="client/client.py",
                                   args=client_args, volumes=volumes,
                                   dimage='mininetfed:client',
                                   env="../env",
                                   numeric_id=i,
                                   mem_limit=client_mem_lim[i],
                                   cpu_shares=cpu_shares[i]
                                   )
                       )

    info('*** Creating links...\n')
    net.connectMininetFedInternalDevices()
    net.addLink(srv1, s1)
    for i, client in enumerate(clients):
        print(bw[i])
        net.addLink(client, s1, cls=TCLink,
                    bw=bw[i], loss=loss[i], delay=delay[i])

    info('*** Starting network...\n')
    net.build()
    net.addNAT(name='nat0', linkTo='s1', ip='192.168.210.254').configDefault()
    s1.start([])

    info('*** Running devices...\n')

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
