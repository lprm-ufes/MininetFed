from containernet.node import DockerSensor


from .common import *


class AutoStop6 (DockerSensor):
    """Node that represents a docker container of a MininerFed client.
    """

    def __init__(self, name, dimage=DEFAULT_IMAGE_6, volumes=[], **kwargs):
        self.name = name
        self.battery_capacity = 10000
        DockerSensor.__init__(self, name, dimage=dimage,
                              volumes=volumes, **kwargs)

        self.cmd("ifconfig eth0 down")

    def auto_stop(self, broker_addr, verbose=True):
        self.cmd("route add -A inet6 default gw  %s" %
                 broker_addr)
        try:
            self.cmd(
                f'bash -c "python3 stop.py {broker_addr}"', verbose=verbose)

        except:
            print(color.BLUE+"\nKeyboard interrupt: manual continue"+color.RESET)
