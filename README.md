# MininetFed

MininetFed is a federated learning environment emulation tool based on Mininet and Containernet.

Its main features include:

- **Addition of new Mininet nodes**: Server, Client. These containerized nodes allow configuration of connection characteristics, available RAM, CPU, etc.
- **Automatic setup of a communication environment using MQTT**
- **Facilitates the implementation of new aggregation and client selection functions**
- **Enables the development of new trainers** to be executed on the clients (model + dataset + manipulations)


# Mailing List  
[https://groups.google.com/forum/#!forum/mininetfed-discuss](https://groups.google.com/g/mininetfed-discuss)

# Getting Started with MininetFed


### Cloning the MininetFed Repository:

```
git clone https://github.com/lprm-ufes/MininetFed
```

## Prerequisites

### Installing ContainerNet

MininetFed requires ContainerNet. Before installing it, install its dependencies using the following command:

```
sudo apt install ansible git aptitude
```

#### Tested ContainerNet Version (Recommended)

The recommended version for full MininetFed functionality can be found in the following repository:

```
git clone https://github.com/ramonfontes/containernet.git
cd containernet
sudo util/install.sh -W
```

### Compiling MininetFed

```bash
cd MininetFed
sudo make install
```

### Generating Docker Images

MininetFed also depends on some preconfigured Docker images. Use the following commands to build these images:

```bash
sudo ./docker/create_images.sh
```

## Installing MininetFed

To install, simply run the installation script:

```bash
sudo ./scripts/install.sh
```

## Running the First Example

A basic example can be executed to test MininetFed's functionality:

```bash
sudo python3 examples/basic.py
```

### Expected Result

After execution starts, two folders are expected to be created: `client_log` and `experiments/basic`.

`client_log` is populated with client error logs, while `experiments/basic` contains server error logs, a copy of the `topology` file that generated the experiment, and an experiment log file.

<img src="https://github.com/lprm-ufes/MininetFed/blob/main/imgs/client_log.png" alt="screenshot of client logs folder" />
<img src="https://github.com/lprm-ufes/MininetFed/blob/main/imgs/results.png" alt="screenshot of experiment folder" />

A few seconds after execution starts, several windows are expected to open. These windows include:

- Broker (brk)
- Server (srv1)
- Clients from 0 to 7 (sta0, sta1 ... stax)

<img src="https://github.com/lprm-ufes/MininetFed/blob/main/imgs/execution.png" alt="screenshot of opened windows" />

After execution ends, all windows will close automatically. The results can be checked in the log file idevelopment.

# Documentation

https://github.com/lprm-ufes/MininetFed/tree/development/docs

# Troubleshooting

If any problems occur during execution, use the following command to delete the containers and clean up Mininet:

```bash
mnf_clean
```

After cleaning, try running it again.

# How to Cite

If you use MininetFed in your research or work, please cite the following paper:

```
@inproceedings{sarmento2024mininetfed,  
  title={MininetFed: A tool for assessing client selection, aggregation, and security in Federated Learning},  
  author={Sarmento, Eduardo MM and Bastos, Johann JS and Villaca, Rodolfo S and Comarela, Giovanni and Mota, Vin{\'\i}cius FS},  
  booktitle={2024 IEEE 10th World Forum on Internet of Things (WF-IoT)},  
  pages={1--6},  
  year={2024},  
  organization={IEEE}  
}  
```

# Papers that Used MininetFed

See the complete list of citations [here](docs/en/citations.md).

# Development Team

[Eduardo Sarmento](https://github.com/eduardo-sarmento)  
[Johann Jakob Bastos](https://github.com/jjakob10)  
[João Pedro Batista](https://github.com/joaoBatista04)  
[Ramon Fontes](https://github.com/ramonfontes)  
[Rodolfo Villaça](https://github.com/rodolfovillaca)  
[Vinícius Mota](https://github.com/vfsmota)  

