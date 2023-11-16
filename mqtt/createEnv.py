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
    print("correct use: sudo python3 createEnv.py <requirements.txt>")
    exit()
 
REQUIREMENTS = sys.argv[1]


setLogLevel('info')
net = Containernet(controller=Controller)
info('*** Adding controller\n')
net.addController('c0')


volumes = [f"{Path.cwd()}:/flw"]
images = "node:stable"

s1 = net.addSwitch('s1')

info('*** Adicionando Containers\n')
srv1 = net.addDocker('srv1',dimage=images, volumes=volumes, mem_limit="2048m")
net.addLink(srv1,s1)
   
net.start()
info('*** Criando env')
srv1.cmd(f"bash -c 'cd flw && python3 -m venv env' ;", verbose=True)

info('*** Iniciando instalação')
srv1.cmd(f"bash -c 'cd flw && . env/bin/activate && pip install -r {REQUIREMENTS}' ;",verbose=True)
#CLI(net);
info('*** Parando MININET')
net.stop()
