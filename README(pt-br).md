# MininetFed

<img align="left" src="https://github.com/lprm-ufes/MininetFed/blob/main/FED.svg" alt="logo" width="225"/>

O MininetFed é uma ferramenta de emulação de ambientes de aprendizado federado baseada no Mininet e no Containernet.

A suas principais funcionalidades incluem:

- Adição de novos _nodes_ Mininet: Server, Client
  - Esses _nodes_ conteinerizados permitem configurar características de suas conexões, disponibilidade de RAM, CPU etc.
- Definição automática de um ambiente de comunicação por meio de Mqtt
- Facilitar a implementação de novas funções de agregação e de seleção de clientes
- Permitir a implementação de novos treinadores que serão executados nos clientes (modelo + dataset + manipulações)


# Documentação completa

[Link](https://github.com/lprm-ufes/MininetFed/tree/development/docs)


# Primeiros passos com o MininetFed

> **Nota importante**
> Caso esteja utilizando o arquivo OVA no VitrualBox, pule diretamente para [Executar o MininetFed com um exemplo](#executar-o-mininetfed-com-um-exemplo)


## Pré requisitos

### Instalar ContainerNet

A versão recomendada para o uso de todas as funcionalidade do MininetFed pode ser encontrada no seguinte repositório:

```bash
git clone https://github.com/ramonfontes/containernet.git
```

Para instalar, rode os seguintes comandos

```bash
cd containernet
sudo util/install.sh -W
```

> Note que não é mais necessário instalar o docker engine separadamente uma vez que o Containernet na versão indicada já é fornecida com o docker engine.

## Instalação do MininetFed

Clone o repositório do MininetFed

```bash
git clone -b development https://github.com/lprm-ufes/MininetFed.git
```

Para instalar, apenas rode o script de instalação

```bash
sudo ./scripts/install.sh
```

## Rodando o primeiro exemplo

Um primeiro exemplo básico pode ser rodado para testar o funcionamento do MininetFed

```bash
sudo python3 examples/basic/topology.py
```

### Resultado esperado

