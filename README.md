# MiniNetFED

MininetFed is a federated learning environment emulation tool based on Mininet and Containernet.

Its main features include:

- **Addition of new Mininet nodes**: Server, Client. These containerized nodes allow configuration of connection characteristics, available RAM, CPU, etc.
- **Automatic setup of a communication environment using MQTT**
- **Facilitates the implementation of new aggregation and client selection functions**
- **Enables the development of new trainers** to be executed on the clients (model + dataset + manipulations)

# Mailing List  
[https://groups.google.com/forum/#!forum/mininetfed-discuss](https://groups.google.com/g/mininetfed-discuss)

# Getting Started with MiniNetFED

### Cloning the MiniNetFED Repository:

```
git clone -b development https://github.com/lprm-ufes/MininetFed.git
```

## Prerequisites

### Installing ContainerNet
MiniNetFED requires ContainerNet. Before installing it, install its dependencies using the following command:

```
sudo apt-get install ansible git aptitude
```

#### Tested ContainerNet Version (Recommended)

The recommended version for full MiniNetFED functionality can be found in the following repository:

```
git clone https://github.com/ramonfontes/containernet.git
cd containernet
sudo util/install.sh -W
```

### Generating Docker Images

MiniNetFED also depends on some preconfigured Docker images. Use the following commands to build these images:

```bash
cd containernet
sudo ./docker/create_images.sh
```

## Running the First Example

A basic example can be executed to test MininetFed's functionality:

```bash
sudo python3 examples/basic/topology.py
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

> **Important Warning:** The cleaning script may affect other Docker containers running on the same machine that are **not** related to MininetFed.
>
> Ensure beforehand that nothing important is running in containers before proceeding with the script execution.
