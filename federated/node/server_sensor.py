from containernet.node import DockerSensor
try:
    from containernet.term import makeTerm
except:
    from mininet.term import makeTerm

import json

from .common import *


class ServerSensor (DockerSensor):
    """Node that represents a docker container of a MininerFed server.
    """

    def __init__(self, name, script, args={}, dimage=None, cpu_quota=None, volumes=[], mem_limit=None, **kwargs):
        self.script = script
        self.args = args
        # self.env = env

        if cpu_quota is not None:
            kwargs["cpu_period"] = CPU_PERIOD
            kwargs["cpu_quota"] = cpu_quota

        if 'battery_capacity' in kwargs:
            self.battery_capacity = kwargs['battery_capacity']

        super().__init__(name, dimage=dimage,
                         volumes=volumes, mem_limit=mem_limit, **kwargs)

        # self.cmd("ifconfig eth0 down")
        # funcionar como gateway
        self.cmd("iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE")

    def run(self, broker_addr, experiment_controller):
        self.experiment = experiment_controller
        self.broker_addr = broker_addr
        # super().start()
# . {ENVS_FOLDER}/{self.env}/bin/activate &&
        cmd = f"""bash -c "python3 {self.script} {self.broker_addr} {self.experiment.getFileName()} 2> {self.experiment.getFileName(extension='''''')}_err.txt """

        if self.args != None and len(self.args) != 0:
            json_str = json.dumps(self.args).replace('"', '\\"')
            cmd += f"'{json_str}'"
        cmd += '" ;'

        # funcionar como gateway
        # self.cmd("route add default gw %s" %
        #          self.broker_addr)

        makeTerm(self, cmd=cmd)

    def auto_stop(self, verbose=True):
        try:
            self.cmd(
                f'bash -c "cd {VOLUME_FOLDER} && python3 stop.py {self.broker_addr}"', verbose=verbose)

        except:
            print(color.BLUE+"\nKeyboard interrupt: manual continue"+color.RESET)
