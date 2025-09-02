import os
import sys
from collections import OrderedDict
from analysis.config import Config
from analysis.process_log import File
from analysis.generate_graphics import Graphics
from analysis.dataset_analysis_graphics import DatasetAnalysisGraphics

DATASET_ANALYSIS = True

try:
    from examples.client import Trainer
except Exception as inst:
    print("Unable to import Trainer. Dataset analysis charts (datasets_analysis) are disabled")
    print(type(inst))
    print(inst.args)
    print(inst)
    DATASET_ANALYSIS = False


def analysis(analysis_yaml_path):
    config = Config(analysis_yaml_path)
    experiments_analysis = config.get("experiments_analysis")
    FOLDER = config.get("experiments_folder")

    if experiments_analysis is not None:

        csv = experiments_analysis.get("save_csv")
        dfs = []

        for experiment in experiments_analysis["from"]:
            exp_files = experiment.get("files")
            experiment_name = experiment["experiment"]
            alias = experiment.get("alias")
            if exp_files != None:
                for idx, fileName in enumerate(exp_files):
                    name = None
                    filepath = f"{experiment_name}/{fileName.split('.')[0]}"

                    if alias is not None:
                        exp_alias = alias
                        if idx == 0:
                            name = alias
                        else:
                            name = f"{alias} ({idx})"
                    else:
                        exp_alias = experiment_name
                        name = filepath

                    f = File(f"{FOLDER}/{filepath}")
                    df = f.get_dataframe()
                    netdf = f.get_net_dataframe()
                    if csv:
                        f.save_to_csv()
                    dfs.append(
                        {'name': name, 'experiment': exp_alias, 'df': df, 'netdf': netdf, 'from_yaml': experiment})
            else:
                idx = 0
                for fileName in os.listdir(f"{FOLDER}/{experiment_name}"):
                    if fileName.endswith(".log"):
                        name = None
                        filepath = f"{experiment_name}/{fileName.split('.')[0]}"

                        if alias is not None:
                            exp_alias = alias
                            if idx == 0:
                                name = alias
                            else:
                                name = f"{alias} ({idx})"
                        else:
                            exp_alias = experiment_name
                            name = filepath

                        f = File(f"{FOLDER}/{filepath}")
                        df = f.get_dataframe()
                        netdf = f.get_net_dataframe()
                        if csv:
                            f.save_to_csv()
                        dfs.append(
                            {'name': name, 'experiment': exp_alias, 'df': df, 'netdf': netdf, 'from_yaml': experiment})
                        idx += 1

        plot = Graphics(dfs, experiments_analysis.get("save_graphics"), FOLDER)

        for graphic in experiments_analysis["graphics"]:
            if graphic['type'] == 'total_energy_consumption':
                plot.total_energy_consumption()
            elif graphic['type'] == 'total_energy_consumption_all':
                plot.total_energy_consumption_all()
            elif graphic['type'] == 'total_energy_consumption_centrais':
                plot.energy_consumption_centrais()
            elif graphic['type'] == 'energy_consumption':
                plot.energy_consumption()
            elif graphic['type'] == 'mean_acc':
                plot.mean_acc()
            elif graphic['type'] == 'mean_acc_k_folds':
                plot.mean_acc_k_folds()
            elif graphic['type'] == 'deltaT_per_round':
                plot.deltaT_per_round()
            elif graphic['type'] == 'n_clients_absolute':
                plot.n_clients_absolute()
            elif graphic['type'] == 'n_clients_relative':
                relative_to = f"{graphic['relative_to']['experiment']}/{graphic['relative_to']['file'].split('.')[0]}"
                plot.n_clients_relative(relative_to)
            elif graphic['type'] == 'network_consumption':
                plot.network_consumption()

    datasets_analysis = config.get("datasets_analysis")
    if datasets_analysis != None and DATASET_ANALYSIS:
        trainers = OrderedDict()
        for id in datasets_analysis["id"]:
            trainers[id] = Trainer(id, datasets_analysis["mode"])
        plot = DatasetAnalysisGraphics(trainers, datasets_analysis["mode"])

        for graphic in datasets_analysis["graphics"]:
            # Distribuição de classes
            if 'class_distribution_per_client' == graphic["type"]:
                plot.class_distribution(graphic.get("y_labels"))

            if 'class_distribution_complete' == graphic["type"]:
                plot.class_distribution_all(graphic.get("y_labels"))

            # Histograma
            if 'histogram' == graphic["type"]:
                plot.histogram()

            # Boxplot
            if 'boxplot' == graphic["type"]:
                plot.boxplot()

            # Matriz de correlação
            if 'correlation_matrix' == graphic["type"]:
                plot.correlation_matrix()


if __name__ == '__main__':
    n = len(sys.argv)

    if n < 2:
        # print("correct use: sudo python3 analysis.py <experiments_folder> <graphics.yaml>")
        print("alternative: correct use: sudo python3 analysis.py <graphics.yaml> ...")
        exit()

    for analysis_yaml_path in sys.argv[1:]:
        analysis(analysis_yaml_path)
