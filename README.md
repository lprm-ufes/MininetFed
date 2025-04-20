# MininetFed

<img align="left" src="https://github.com/lprm-ufes/MininetFed/blob/main/FED.svg" alt="logo" width="225"/>

MininetFed is a tool for emulating federated learning environments based on Mininet and Containernet.

Its main features include:

- Adding new Mininet nodes: Server, Client
  - These containerized nodes allow configuring connection characteristics, RAM availability, CPU, etc.
- Automatic definition of a communication environment via MQTT
- Facilitating the implementation of new aggregation and client selection functions
- Allowing the implementation of new trainers to be executed on clients (model + dataset + manipulations)

# Full Documentation

[Link](https://github.com/lprm-ufes/MininetFed/tree/main/docs)

# Getting Started with MininetFed

> **Important Note**
> If you are using the OVA file in VirtualBox, skip directly to [Running MininetFed with an Example](#running-mininetfed-with-an-example)

## Prerequisites

### Install Containernet

The recommended version for using all MininetFed features can be found in the following repository:

```bash
git clone https://github.com/ramonfontes/containernet.git
```

To install, run the following commands:

```bash
cd containernet
sudo util/install.sh -W
```

> Note that it is no longer necessary to install Docker Engine separately, as the recommended version of Containernet already includes Docker Engine.

## Installing MininetFed

Clone the MininetFed repository:

```bash
git clone -b development https://github.com/lprm-ufes/MininetFed.git
```

To install, simply run the installation script:

```bash
sudo ./scripts/install.sh
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

After execution ends, all windows will close automatically. The results can be checked in the log file idevelopment
If any issues occur during execution, use the following command to delete containers and clean Mininet:

```bash
mnf_clean
```

After cleaning, try running it again.

> **Important Warning:** The cleaning script may affect other Docker containers running on the same machine that are **not** related to MininetFed.
>
> Ensure beforehand that nothing important is running in containers before proceeding with the script execution.
