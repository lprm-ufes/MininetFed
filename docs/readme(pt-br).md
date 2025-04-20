# Versão da documentação

v1.0.1

# MiniNetFED

<img align="left" src="https://github.com/lprm-ufes/MininetFed/blob/main/FED.svg" alt="logo" width="200"/>
O MininetFed é uma ferramenta de emulação de ambientes de aprendizado federado baseada no Mininet e no Containernet.

As suas principais funcionalidades incluem:

- Adição de novos _nodes_ Mininet: Server, Client
  - Esses _nodes_ containerizados permitem configurar características de suas conexões, disponibilidade de RAM, CPU etc.
- Definição automática de um ambiente de comunicação por meio de MQTT
- Facilitar a implementação de novas funções de agregação e de seleção de clientes
- Permitir a implementação de novos treinadores que serão executados nos clientes (modelo + dataset + manipulações)

# Paginas (pt-br)

- [Clientes](pt-br/Clientes.md)
- [Script de análise](pt-br/Script-de-análise.md)
- [Servidor](pt-br/Servidor.md)

# Pages (en)

- [Analysis script](en/Analysis-script.md)
- [Clients](en/Clients.md)
- [Server](en/Server.md)
