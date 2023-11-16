from containernet.cli import CLI
from containernet.link import TCLink
from containernet.net import Containernet
from mininet.node import Controller
from mininet.log import info, setLogLevel
from containernet.term import makeTerm
from pathlib import Path
import time
from Config import Config
import sys

# total args
n = len(sys.argv)

# check args
if (n != 2):
    print("correct use: sudo python3 run.py <config.yaml>")
    exit()

CONFIGYAML = sys.argv[1]

setLogLevel('info')
info('*** Importing configurations\n')

# endereço do arquivo de configurações
config = Config(CONFIGYAML)

general = config.get("general")
absolute = general["absolute_path"]
n_cpu = general["n_available_cpu"]
broker_image = general["broker_image"]

server = config.get("server")
server_volumes = ""
server_script = ""
server_quota = server["vCPU_percent"] * n_cpu * 1000

server_volumes = [f"{Path.cwd()}:" + server["volume"]]

# if absolute:
#     server_script = [f"{Path.cwd()}" + server["script"]]
# else:
#     server_script = server['script']

server_images = server["image"]


net = Containernet(controller=Controller)
info('*** Adding controller\n')
net.addController('c0')

info('*** Adicionando SWITCHS\n')
s = list()
for i in range(1, config.get("network_components") + 1):
    s.append(net.addSwitch(f"s{i}"))


info('*** Adicionando Containers\n')
# broker container
broker = net.addDocker('brk1', dimage=broker_image,
                       volumes=server_volumes,  mem_limit="128mb")
net.addLink(broker, s[server["conection"] - 1])

# server container
srv1 = net.addDocker('srv1', dimage=server_images, volumes=server_volumes,
                     mem_limit=server["memory"], cpu_quota=server_quota)
net.addLink(srv1, s[server["conection"] - 1])


# client containers
clientes = list()
cont = 0
qtdDevice = 0
for client_type in config.get("client_types"):
    for x in range(1, client_type["amount"]+1):
        volumes = ""
        if absolute:
            volumes = client_type["volume"]
        else:
            volumes = [f"{Path.cwd()}:" + client_type["volume"]]
        qtdDevice += 1
        client_quota = client_type["vCPU_percent"] * n_cpu*1000
        d = net.addDocker(f'sta{client_type["name"]}{x}', cpu_quota=client_quota,
                          dimage=client_type["image"], volumes=volumes,  mem_limit=client_type["memory"])
        net.addLink(d, s[client_type['conection'] - 1],
                    loss=client_type["loss"], bw=client_type["bw"])
        clientes.append(d)
        cont = (cont+1) % 16


info('*** Configurando Links\n')

net.start()

BROKER_ADDR = "172.17.0.2"
MIN_TRAINERS = 2
TRAINERS_PER_ROUND = 3
NUM_ROUNDS = 10
STOP_ACC = 1.0

print(broker.IP())


makeTerm(broker, cmd="bash -c 'mosquitto -c /flw/mosquitto.conf'")
time.sleep(2)
tScrip = server["script"]
info('*** Subindo servidor\n')
cmd = f"bash -c '. flw/env/bin/activate && python3 flw{tScrip} {BROKER_ADDR} {MIN_TRAINERS} {TRAINERS_PER_ROUND} {NUM_ROUNDS} {STOP_ACC} flw/meu_arquivo.log' ;"
print(cmd)
makeTerm(srv1, cmd=cmd)
time.sleep(3)

cont = 0

for client_type in config.get("client_types"):
    for x in range(1, client_type["amount"]+1):
        info(f"*** Subindo cliente {str(cont+1).zfill(2)}\n")
        cmd = f"bash -c '. flw/env/bin/activate && python3 flw{client_type['script']} {BROKER_ADDR} {clientes[cont].name}' ;"
        print(cmd)
        makeTerm(clientes[cont], cmd=cmd)
        cont += 1

info('*** Rodando CLI\n')
CLI(net)
info('*** Parando MININET')
net.stop()