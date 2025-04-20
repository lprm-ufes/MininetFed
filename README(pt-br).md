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

[Link](https://github.com/lprm-ufes/MininetFed/tree/main/docs)

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

Após a inicialização da execução, é esperada a criação de duas pastas: `client_log` e `experiments/basic`.

`client_log` é populada com os logs de erro dos clientes, enquanto `experiments/basic` apresenta os logs de erro do servidor, uma cópia do arquivo topology que gerou o experimento, e um arquivo de log do experimento.

<img src="https://github.com/lprm-ufes/MininetFed/blob/main/imgs/client_log.png" alt="print da pasta dos logs dos clientes" />
<img  src="https://github.com/lprm-ufes/MininetFed/blob/main/imgs/results.png" alt="print da pasta do exeperimento" />

Alguns segundos após o início da execução, é esperado que se abra várias janelas. Essas janelas são as seguintes:

- broker (brk)
- server (srv1)
- clientes de 0 a 7 (sta0, sta1 ... stax)

<img  src="https://github.com/lprm-ufes/MininetFed/blob/main/imgs/execution.png" alt="print das janelas abertas" />

Após o fim da execução, todas as janelas fecharão automaticamente. Os resultados podem ser conferidos no arquivo de log na pasta `experiments/basic` citada anteriormente.

# Solução de problemas

Caso algum problema ocorra durante a execução, use o seguinte comando para deletar os containers e limpar o mininet:

```bash
mnf_clean
```

Após a limpeza, tente executar novamente.

> **Aviso importante:** O script de limpeza possivelmente afetará outros containers docker em execução na mesma máquina que **não** têm relação com o MininetFed.
>
> Garanta de antemão que não há nada importante executando em containers antes de prosseguir com a execução do script.
