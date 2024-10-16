try:
    from containernet.net import Containernet
    from containernet.term import makeTerm
    from containernet.cli import CLI
except:
    from mininet.net import Containernet
    from mininet.term import makeTerm
    from mininet.cli import CLI
from mininet.node import Controller
from mininet.log import info, setLogLevel
from pathlib import Path
import sys

# total args
n = len(sys.argv)
 
# check args
if (n != 3):
    print("correct use: sudo python3 create_env.py <image> <requirements.txt>")
    exit()

images = sys.argv[1] 
REQUIREMENTS = sys.argv[2]


setLogLevel('info')
net = Containernet(controller=Controller)
info('*** Adding controller\n')
net.addController('c0')


volumes = [f"{Path.cwd()}:/flw"]
# images = "johann:mqtt"

s1 = net.addSwitch('s1')

info('*** Adicionando Containers\n')
srv1 = net.addDocker('srv1',dimage=images, volumes=volumes, mem_limit="2048m")
net.addLink(srv1,s1)
   
net.start()
info('*** Criando env')
srv1.cmd(f"bash -c 'cd flw && python3 -m venv env' ;", verbose=True)

info('*** Iniciando instalação')
srv1.cmd(f"bash -c 'cd flw && . env/bin/activate && pip install -r {REQUIREMENTS}' ;",verbose=True)
# CLI(net)
info('*** Parando MININET')
net.stop()
