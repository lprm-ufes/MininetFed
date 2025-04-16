from containernet.node import DockerSensor
try:
    from containernet.term import makeTerm
except:
    from mininet.term import makeTerm

import json


from .common import *


class ClientSensor (DockerSensor):
    """Node that represents a docker container of a MininerFed client.
    """

    def __init__(self, name, script, numeric_id, args={}, dimage=None, cpu_quota=None, volumes=[], mem_limit=None, **kwargs):
        self.name = name
        # self.trainer_mode = args['mode']
        self.numeric_id = numeric_id
        self.script = script
        self.args = args

        if cpu_quota is not None:
            kwargs["cpu_period"] = CPU_PERIOD
            kwargs["cpu_quota"] = cpu_quota

        if 'battery_capacity' in kwargs:
            self.battery_capacity = kwargs['battery_capacity']
            self.remaining_capacity = 10000

        DockerSensor.__init__(self, name, dimage=dimage,
                              volumes=volumes, mem_limit=mem_limit, **kwargs)

        self.cmd("ifconfig eth0 down")

    def run(self, broker_addr, experiment_controller):
        self.experiment = experiment_controller
        self.broker_addr = broker_addr
        # DockerSensor.start(self) {self.trainer_mode}
        cmd = f"""bash -c "python3 {self.script} {self.broker_addr} {self.name} {self.numeric_id} 2> {VOLUME_FOLDER}/client_log/{self.name}.txt """

        if self.args != None and len(self.args) != 0:
            json_str = json.dumps(self.args).replace('"', '\\"')
            cmd += f"'{json_str}'"
        cmd += '" ;'

        self.cmd("route add -A inet6 default gw  %s" %
                 self.broker_addr)
        print(f"cmd:{cmd}")
        makeTerm(self, cmd=cmd)
