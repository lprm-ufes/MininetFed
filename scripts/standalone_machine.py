from containernet.net import Containernet
from mininet.node import Controller
from mininet.log import info, setLogLevel
from containernet.term import makeTerm
from pathlib import Path
import sys
from containernet.cli import CLI

# total args
n = len(sys.argv)
 
# check args
if (n != 2):
    print("Default image: mininetfed:client")
    print("use suggestion: sudo python3 create_env.py <image>")
   

images = sys.argv[1] 


setLogLevel('info')
net = Containernet(controller=Controller)
info('*** Adding controller\n')
net.addController('c0')


volumes = [f"{Path.cwd()}:/flw"]


s1 = net.addSwitch('s1')

info('*** Adicionando Containers\n')
srv1 = net.addDocker('srv1',dimage=images, volumes=volumes, mem_limit="2048m")
net.addLink(srv1,s1)
   
net.start()

CLI(net)
info('*** Parando MININET')
net.stop()