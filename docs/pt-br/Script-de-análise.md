# Script de análise

Junto ao MininetFed, é fornecido um script python para realizar as análises dos resultados.

# Pré requisitos

## Criação e ativação do env

Rode o script para a criação do environment python com as dependências corretas

```
./scripts/analysis_env.sh
```

Ative o environment com o seguinte comando

```
. analysis_env/bin/activate
```

# Execução

Exemplo padrão

```
cd util
python3 analysis.py analysis.yaml
```

Exemplo geral

```
cd util
python3 analysis.py (analysis_configuration.yaml)
```

# Arquivo de configuração da análise

## Arquivo de exemplo

```jsx
experiments_folder: experiments

experiments_analysis:
  save_csv: true
  save_graphics: true # não implementado

  from:
    - experiment: 04_02_2024fed_sec_per_har
      alias: experimento fed per sec
      files:
        - 20h29m32sfed_sec_per_har.log

    - experiment: 05_02_2024fed_sec_per_har #implicitly get all .log files from the folder
    - experiment: 06_02_2024fed_sec_per_har
    - experiment: 06_02_2024fed_sec_per_mnist

  graphics:
    - type:
		- type: (...)

datasets_analysis:
  id: 0
  mode: client
  graphics:
    - type: class_distribution
    - type: histogram
    - type: boxplot
    - type: correlation_matrix
```

## Estrutura principal

O arquivo de configuração do script de análise é dividido nas seguintes seções

```jsx
experiments_folder: (pasta contendo as subpastas de cada experimento)
experiments_analysis:
datasets_analysis:
```

## experiments_analysis

Essa é a parte da análise dedicada a analisar os resultados de um experimento. Ela é dividida nas seguintes

```jsx
  save_csv: (true or false)
  save_graphics: (true or false)
  from:
    - experiment: (experiment_name)
      alias: (apelido para o experimento) (opcional)
      files: (opcional)
        - (file.log)
				- (...)
		- experiment: (other_experiment_name)
		- (...)

  graphics:
	 - type: (graphic_type)
	 - type: (other_graphic_type_with_params)
		 (param1): (value)
		 (param2): (value)
		 (...)
	 - type: (...)
```

### save_csv

Se verdadeiro, salva os arquivos .csv com as informações do experimento obtidas a partir do log. Isso pode ser útil caso você deseje usar esses dados em outras ferramentas de análise de dados.

### save_graphics (incompleto)

### from

Uma lista das fontes de dados. Indica de quais experimentos e arquivos se deseja extrair as informações para a análise.

Cada subitem **experiment** indica o nome de um experimento. Colocar apenas o nome faz com que todos os arquivos .log sejam importados para a análise, mas ainda é possível adicionar a key **files** e fornecer uma lista de arquivos .log que se deseja considerar.

### graphics

Recebe uma lista de types, onde cada item representa uma plotagem de um gráfico.

Alguns tipos de gráficos exigem parâmetros adicionais. Esses podem ser incluidos como chaves junto ao tipo do gráfico como no exemplo dado anteriormente.

## datasets_analysis

Esse subitem é dedicado as configurações da análise exploratória do dataset recebido por um cliente específico.

### Pré configuração

O script de análise importa o mesmo trainer que o MininetFed utiliza, logo é importante pré configurar qual Trainer será analisado. Para isso, consulte como selecionar um trainer no cliente.

### Estrutura

```jsx
datasets_analysis:
  id: (int 0 - N)
  mode: (client_mode (string))
  graphics:
	 - type: (graphic_type)
	 - type: (other_graphic_type_with_params)
		 (param1): (value)
		 (param2): (value)
		 (...)
	 - type: (...)
```

### id

O id é o valor inteiro recebido pelo Cliente do MininetFed. Esse valor é utilizado como base para a divisão do dataset quando essa é realizada por cada cliente. É possível, portanto, selecionar de qual cliente se deseja analisar os dados.

### mode

É o mesmo mode do config.yaml do MininetFed. É utilizado para selecionar o modo de operação e divisão de dados do cliente.

### graphics

Recebe uma lista de types, onde cada item representa uma plotagem de um gráfico.

Alguns tipos de gráficos exigem parâmetros adicionais. Esses podem ser incluidos como chaves junto ao tipo do gráfico como no exemplo dado anteriormente.

# Gráficos disponíveis por padrão

## Delta T por round

## Acurácia média

## Número de clientes absoluto

## Número de clientes relativo

## Consumo de rede
