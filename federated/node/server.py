from containernet.node import Docker
try:
    from containernet.term import makeTerm
except:
    from mininet.term import makeTerm

import json

from .common import *


class Server (Docker):
    """Node that represents a docker container of a MininerFed server.
    """

    def __init__(self, name, script, args={}, dimage=None, cpu_quota=None, volumes=[], mem_limit=None, **kwargs):
        self.script = script
        self.args = args

        if cpu_quota is not None:
            kwargs["cpu_period"] = CPU_PERIOD
            kwargs["cpu_quota"] = cpu_quota

        Docker.__init__(self, name, dimage=dimage,
                        volumes=volumes, mem_limit=mem_limit, **kwargs)

        self.cmd("ifconfig eth0 down")

    def run(self, broker_addr, experiment_controller, args={}):
        self.experiment = experiment_controller
        self.broker_addr = broker_addr

        cmd = f"""bash -c "python3 {self.script} {self.broker_addr} {self.experiment.getFileName()} 2> {self.experiment.getFileName(extension='''''')}_err.txt """

        if self.args != None and len(self.args) != 0:
            json_str = json.dumps(self.args).replace('"', '\\"')
            cmd += f"'{json_str}'"
        cmd += '" ;'
        self.cmd("route add default gw %s" %
                 self.broker_addr)

        makeTerm(self, cmd=cmd)
