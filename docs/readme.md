# Documentation Version

v1.0.1

# MininetFed

<img align="left" src="https://github.com/lprm-ufes/MininetFed/blob/main/FED.svg" alt="logo" width="200"/>
MininetFed is a federated learning environment emulation tool based on Mininet and Containernet.

Its main features include:

- Addition of new Mininet nodes: Server, Client
  - These containerized nodes allow configuring characteristics of their connections, RAM availability, CPU, etc.
- Automatic definition of a communication environment via MQTT
- Facilitating the implementation of new aggregation and client selection functions
- Allowing the implementation of new trainers to be executed on the clients (model + dataset + manipulations)

# Pages (en)

- [Analysis script](en/Analysis-script.md)
- [Clients](en/Clients.md)
- [Server](en/Server.md)
