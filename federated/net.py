
from containernet.net import Containernet
from containernet.cli import CLI

from federated.node import Broker, AutoStop, AutoStop6
from federated.experiment import Experiment

from mn_wifi.sixLoWPAN.link import LoWPAN


class MininetFed(Containernet):

    def __init__(self, experiment_name, experiments_folder, default_volumes,
                 default_connection='s1', date_prefix=False, broker_mode="internal",
                 ext_broker_ip='127.0.0.1', topology_file=None, **kwargs):

        self.broker_addr = None
        self.apsensor = None
        self.auto_stop = None
        self.brk = None
        self.default_connection = default_connection
        self.ext_broker_ip = ext_broker_ip
        self.broker_mode = broker_mode

        self.nodes = {}
        self.priority_nodes = []
        self.default_volumes = default_volumes
        self.experiment_controller = Experiment(experiment_name=experiment_name,
                                                experiments_folder=experiments_folder,
                                                create_new=date_prefix)
        if topology_file is not None:
            self.experiment_controller.copyFileToExperimentFolder(
                topology_file)
        super().__init__(**kwargs)
        self.configureMininetFedInternalDevices()

    def addAutoStop6(self):
        self.auto_stop = self.addSensor('auto_stop', privileged=True,
                                        environment={"DISPLAY": ":0"},
                                        cls=AutoStop6,
                                        ip6=f'fe80::fffe/64', volumes=self.default_volumes,
                                        dimage="mininetfed:auto_wait6"
                                        )

    def addLinkAutoStop(self, device2):
        self.addLink(self.auto_stop, device2, cls=LoWPAN)

    def addFlHost(self, name, cls=None, start_priority=0, **params):
        """
        Adds a host to the 'nodes' structure based on priority.
        Each priority is represented by a list containing the associated hosts.
        """

        # Make sure the priority exists in the dictionary
        if start_priority not in self.nodes:
            self.nodes[start_priority] = []

        # Add the host from the list corresponding to the priority
        host = super().addSensor(name, cls, **params)
        self.nodes[start_priority].append(host)
        return host

    def addAPSensor(self, name, cls=None, **params):
        self.apsensor = super().addAPSensor(name, cls, **params)
        return self.apsensor

    def configureMininetFedInternalDevices(self):
        self.brk = super().addHost('brk', cls=Broker, mode=self.broker_mode,
                                   ext_broker_ip=self.ext_broker_ip,
                                   volumes=self.default_volumes,
                                   dimage="mininetfed:broker")

        self.auto_stop = super().addHost('stop', cls=AutoStop,
                                         volumes=self.default_volumes,
                                         dimage="mininetfed:auto_wait")

    def connectMininetFedInternalDevices(self, connection="s1"):
        self.addLink(connection, self.brk)
        self.addLink(connection, self.auto_stop)

    def runFlDevices(self):
        # Runs the broker and initializes other components
        self.brk.run()

        # Get the broker address
        self.broker_addr = self.brk.IP(intf="brk-eth0")

        # Perform additional services using the broker address
        self.auto_stop.run(broker_addr=self.broker_addr)

    def wait_experiment(self, start_cli=False):
        if start_cli:
            CLI(self)
        else:
            self.auto_stop.auto_stop(self.broker_addr)
