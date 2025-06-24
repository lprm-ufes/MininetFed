Here is the translated text:

**Analysis Script**

Along with MininetFed, a Python script is provided to perform analyses on results.

**Prerequisites**

## Creating and activating the environment

Run the script to create the Python environment with the correct dependencies

```
./scripts/analysis_env.sh
```

Activate the environment with the following command

```
. analysis_env/bin/activate
```

**Execution**

Example standard

```
cd util
python3 analysis.py analysis.yaml
```

General example

```
cd util
python3 analysis.py (analysis_configuration.yaml)
```

**Analysis Configuration File**

## Example file

```yml
experiments_folder: experiments

experiments_analysis:
  save_csv: true
  save_graphics: true # not implemented

  from:
    - experiment: 04_02_2024fed_sec_per_har
      alias: fed per sec experiment
      files:
        - 20h29m32sfed_sec_per_har.log

    - experiment: 05_02_2024fed_sec_per_har # implicitly get all .log files from the folder
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

## Main Structure

The analysis script configuration file is divided into the following sections:

```yml
experiments_folder: (folder containing subfolders for each experiment)
experiments_analysis:
datasets_analysis:
```

## experiments_analysis

This section is dedicated to analyzing results from an experiment. It is divided into the following subsections:

```yml
  save_csv: (true or false)
  save_graphics: (true or false)
  from:
    - experiment: (experiment_name)
      alias: (optional nickname for the experiment)
      files: (optional)
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

```

### save_csv

If true, saves CSV files with experiment information obtained from the log. This can be useful if you want to use these data in other data analysis tools.

### save_graphics (incomplete)

### from

A list of data sources. Indicates which experiments and files to extract information for analysis.

Each subitem **experiment** indicates an experiment name. Placing only the name makes all .log files imported for analysis, but it's still possible to add the key **files** and provide a list of .log files to consider.

### graphics

Receives a list of types, where each item represents a plotting of a graph.

Some graphic types require additional parameters. These can be included as keys along with the graphic type as in the example given above.

## datasets_analysis

This section is dedicated to configuration for exploratory analysis of the dataset received by a specific client.

### Pre-configuration

The analysis script imports the same trainer used by MininetFed, so it's essential to pre-configure which Trainer will be analyzed. For this, consult how to select a trainer in the client.

### Structure

```yml
datasets_analysis:
  id: (int 0 - N)
  mode: (client_mode (string))
  graphics:
	 - type: (graphic_type)
	 - type: (other_graphic_type_with_params)
		 (param1): (value)
		 (param2): (value)
		 (...)

```

### id

The id is the integer value received by the MininetFed client. This value is used as a basis for dividing the dataset when it is performed by each client. It's possible to select which client you want to analyze data from.

### mode

This is the same mode as in config.yaml of MininetFed. It is used to select the operation and data division mode of the client.

### graphics

Receives a list of types, where each item represents a plotting of a graph.

Some graphic types require additional parameters. These can be included as keys along with the graphic type as in the example given above.

# Available graphs by default

## Delta T per round

## Average accuracy

## Absolute number of clients

## Relative number of clients

## Network consumption