import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from itertools import zip_longest
import math
from collections import OrderedDict


linestyles = [
    ('dashdotted',            (0, (3, 5, 1, 5))),
    ('dashed',                (0, (5, 5))),
    ('densely dotted',        (0, (1, 1))),
    ('dotted',                (0, (1, 5))),
    ('long dash with offset', (5, (10, 3))),

    ('loosely dashed',        (0, (5, 10))),
    ('densely dashed',        (0, (5, 1))),

    ('loosely dashdotted',    (0, (3, 10, 1, 10))),
    ('densely dashdotted',    (0, (3, 1, 1, 1))),

    ('loosely dashdotdotted', (0, (3, 10, 1, 10, 1, 10))),
    ('dashdotdotted',         (0, (3, 5, 1, 5, 1, 5))),
    ('loosely dotted',        (0, (1, 10))),
    ('densely dashdotdotted', (0, (3, 1, 1, 1, 1, 1)))]


class Graphics:
    def __init__(self, data_frames, save, experiments_folder):
        self.dfs = data_frames
        self.save = save  # salva gráficos (não implementado)
        self.experiments_folder = experiments_folder
        # dfs = [{'name': name, 'df': df} for name, df in zip(names, data_frames)]

    #     # Gráfico 1: Delta T vs Round
    # def deltaT_per_round(self):
    #     plt.figure(figsize=(10, 6))
    #     for item in self.dfs:
    #         df = item['df']
    #         plt.plot(df['round'], df['deltaT'], label=item['name'])

    #     plt.xlabel('round')
    #     plt.ylabel('Delta T (milisegundos)')
    #     plt.title('Gráfico de Delta T vs round')
    #     plt.legend()
    #     plt.show()

    #     # Gráfico 2: acurácia média vs round
    # def mean_acc(self):
    #     # plt.clf()
    #     plt.figure(figsize=(10, 6))
    #     for item in self.dfs:
    #         df = item['df']
    #         # for column in df.columns[2:]:  # Ignorando as colunas 'round' e 'round Delta T'
    #         plt.plot(df['round'], df['mean_accuracy'], label=item['name'])
    #     plt.xlabel('round')
    #     plt.ylabel('Acurácia')
    #     plt.title('Gráfico de Acurácia vs round')
    #     plt.legend()
    #     plt.show()

    def n_clients_absolute(self):
        # plt.clf()
        plt.figure(figsize=(10, 6))
        for item in self.dfs:
            df = item['df']
            # for column in df.columns[2:]:  # Ignorando as colunas 'round' e 'round Delta T'
            plt.plot(df['round'], df['n_selected'], label=item['name'])
        plt.xlabel('round')
        plt.ylabel('N clientes selecionados')
        plt.title('Número de clientes selecionados por round')
        plt.legend()
        plt.show()

    def n_clients_relative(self, relative_to):
        if len(self.dfs) > 1:
            # plt.clf()
            plt.figure(figsize=(10, 6))
            ref_item = next(
                (d for d in self.dfs if d['name'] == relative_to), None)
            ref_df = ref_item['df']
            for item in self.dfs:
                if item['name'] == ref_item['name']:
                    continue
                df = item['df']
                plt.plot(df['round'], ref_df['n_selected'] -
                         df['n_selected'], label=item['name'])

            # Adicionando uma linha pontilhada em Y=0
            plt.axhline(0, color='black', linestyle='dashed')

            # Definindo a escala de Y para números inteiros
            y_min = int(min(ref_df['n_selected'] - df['n_selected']))
            y_max = int(max(ref_df['n_selected'] - df['n_selected']))
            plt.yticks(np.arange(y_min, y_max+1, step=1))

            plt.xlabel('round')
            plt.ylabel('Diferença no Nº clientes selecionados')
            plt.title(
                f'Gráfico de Nº clientes selecionados relativo à "{ref_item["name"]}"')
            plt.legend()
            plt.show()

    # def network_consumption(self):
    #     plt.figure(figsize=(10, 6))
    #     for item in self.dfs:
    #         df = item['netdf']
    #         plt.scatter(df['segs'], df['recived'], label=item['name'], marker='o', s=20)

    #     plt.xlabel('Tempo de execução (segundos)')
    #     plt.ylabel('bytes recived by the broker')
    #     plt.title('Gráfico de bytes recebidos no decorrer do tempo')
    #     plt.legend()
    #     plt.show()

    def network_consumption(self):
        plt.figure(figsize=(10, 6))
        for item in self.dfs:
            df = item['netdf']
            plt.scatter(df['segs']/60, df['recived']/2**30,
                        label=item['name'], marker='o', s=20)

        plt.xlabel('Execution time (minutes)', fontsize=18)
        plt.ylabel('Training network traffic (GBytes)', fontsize=18)
        plt.legend(fontsize=16)
        plt.tick_params(labelsize=16)
        plt.show()

    # Gráfico 1: Delta T vs Round
    def deltaT_per_round(self):
        plt.figure(figsize=(10, 6))
        for item in self.dfs:
            df = item['df']
            plt.plot(df['round'], df['deltaT'], label=item['name'])

        plt.xlabel('round', fontsize=18)
        plt.ylabel('Delta T (milisegundos)', fontsize=18)
        plt.legend(fontsize=16)
        plt.tick_params(labelsize=16)
        plt.show()

    # Gráfico 2: acurácia média vs round
    def mean_acc(self):
        y_min = 1000
        y_max = -1000
        plt.figure(figsize=(10, 6))
        for idx, item in enumerate(self.dfs):
            df = item['df']

            y_min = min(int(min(df['round'])), y_min)
            y_max = max(int(max(df['round'])), y_max)

            plt.plot(df['round'], df['mean_accuracy'],
                     label=item['name'], linestyle=linestyles[idx % len(linestyles)][1], linewidth=3.4)
            # print(item)

        # name = "Dados iid"
        # name = "Dados balanceados"
        # name = "Dados mid-iid"
        # name = "Dados Parcialmente Desbalanceados"
        # name = "Dados non-iid"
        # name = "Dados Desbalanceados"
        name = item['from_yaml']['chart_title']
        plt.xlabel('Rodada', fontsize=28)
        plt.ylabel('Acurácia', fontsize=28)
        plt.title(f'Comparação de Acurácia por Rodada \n {name}', fontsize=30)
        plt.xticks(np.arange(y_min+1, y_max+1, step=2))
        plt.legend(fontsize=26)
        plt.tick_params(labelsize=26)
        plt.savefig(f"acuracia {name}.eps",
                    bbox_inches='tight')
        plt.show()

    # def energy_consumption(self):
    #     max_val = 0
    #     plt.figure(figsize=(18, 10))
    #     # plt.figure(figsize=(10, 6))
    #     counter = 0
    #     for item in self.dfs:
    #         df = item['df']
    #         for label in df:
    #             if 'energy_consumption' in label and ('sta0' in label or 'sta1' in label):

    #                 # if 'energy_consumption' in label and ('sta0' in label or 'sta4' in label):
    #                 counter += 1
    #                 plt.plot(
    #                     df['round'], df[label], linestyle=linestyles[counter % len(linestyles)][1], label=f"{item['name']} {label.replace('_energy_consumption','').replace('sta','- sensor ')}")
    #                 max_val = max(max_val, df['round'].max())

    #     plt.xlim(1, max_val)
    #     plt.xticks(range(1, max_val + 1))
    #     plt.ylim(0, None)

    #     plt.xlabel('Rodada de treino', fontsize=18)
    #     plt.ylabel('Energia consumida (Wh)', fontsize=18)
    #     plt.title('Consumo de Energia Acumulado por Rodada', fontsize=20)
    #     plt.legend(fontsize=16)
    #     plt.tick_params(labelsize=16)
    #     # plt.show()
    #     plt.savefig("consumo borda vs central.eps", bbox_inches='tight')

    # def energy_consumption_centrais(self):
    #     max_val = 0
    #     plt.figure(figsize=(18, 10))
    #     counter = 0
    #     for item in self.dfs:
    #         df = item['df']
    #         for label in df:
    #             # if 'energy_consumption' in label:
    #             if 'energy_consumption' in label and ('sta0' in label or 'sta4' in label):
    #                 counter += 1

    #                 plt.plot(
    #                     df['round'], df[label], linestyle=linestyles[counter % len(linestyles)][1], label=f"{item['name']} {label.replace('_energy_consumption','').replace('sta','- sensor ')}")
    #                 max_val = max(max_val, df['round'].max())

    #     plt.xlim(1, max_val)
    #     plt.xticks(range(1, max_val + 1))
    #     plt.ylim(0, None)

    #     plt.xlabel('Rodada de treino', fontsize=18)
    #     plt.ylabel('Energia consumida (Wh)', fontsize=18)
    #     plt.title('Consumo de Energia Acumulado por Rodada', fontsize=20)
    #     plt.legend(fontsize=16)
    #     plt.tick_params(labelsize=16)
    #     # plt.show()
    #     plt.savefig("consumo centrais.eps", bbox_inches='tight')

    # def total_energy_consumption(self):
    #     experiment_names = []
    #     total_energies = []

    #     for item in self.dfs:
    #         df = item['df']
    #         energy = 0.0
    #         for label in df:
    #             if 'energy_consumption' in label:
    #                 energy += df[label].sum()

    #         experiment_names.append(item['name'])
    #         total_energies.append(energy)

    #     # Cria o gráfico de barras
    #     # plt.figure(figsize=(10, 6))
    #     plt.figure(figsize=(18, 10))
    #     bars = plt.bar(experiment_names, total_energies,
    #                    color='skyblue', edgecolor='black')

    #     plt.xlabel('Experimento', fontsize=18)
    #     plt.ylabel('Energia Consumida (Wh)', fontsize=18)
    #     plt.title('Consumo Total de Energia por Experimento', fontsize=20)
    #     plt.xticks(fontsize=14)
    #     plt.yticks(fontsize=14)

    #     # Adiciona os valores no topo das barras
    #     for bar, energy in zip(bars, total_energies):
    #         plt.text(bar.get_x() + bar.get_width() / 2,  # Posição X
    #                  bar.get_height(),                   # Posição Y
    #                  f'{energy:.2f}',                    # Texto formatado
    #                  ha='center', va='bottom', fontsize=12)

    #     plt.tight_layout()
    #     # plt.show()
    #     plt.savefig("comparacao consumo total.eps", bbox_inches='tight')

    def total_energy_consumption_all(self):
        count = -1
        space = [' ', '  ', '   ']
        for item in self.dfs:
            plt.figure(figsize=(12, 10))
            df = item['df']
            count += 1
            experiment_names = []
            total_energies = []
            for label in df:
                if 'energy_consumption' in label:

                    experiment_names.append(
                        f"{space[count]}{label.replace('_energy_consumption','').replace('sta','sensor ')}")
                    total_energies.append(df[label].sum())
            # Combina as duas listas em uma lista de tuplas e ordena
            zipped_lists = zip(experiment_names, total_energies)
            sorted_pairs = sorted(zipped_lists)

            # Descompacta a lista ordenada de volta em duas listas
            tuples = zip(*sorted_pairs)
            experiment_names, total_energies = [
                list(tuple) for tuple in tuples]
            bars = plt.bar(experiment_names, total_energies,  # color='blue',
                           edgecolor='black', label=item['name'])

            # Adiciona os valores no topo das barras
            for bar, energy in zip(bars, total_energies):
                plt.text(bar.get_x() + bar.get_width() / 2,  # Posição X
                         bar.get_height(),                   # Posição Y
                         f'{energy:.2f}',                    # Texto formatado
                         ha='center', va='bottom', fontsize=30)

            plt.xlabel('Sensores', fontsize=30)
            plt.ylabel('Energia Consumida (Wh)', fontsize=24)
            plt.title(
                f"Consumo Total de Energia no Experimento \n {item['name']}", fontsize=30, pad=20)
            # plt.xticks(fontsize=14)
            plt.xticks(rotation=45, fontsize=30)  # Rotaciona 45 graus

            plt.yticks(fontsize=30)
            plt.ylim(0, 70)
            # plt.legend(title="Clientes", fontsize=12, title_fontsize=14)

            plt.tight_layout()
            plt.savefig(f"consumo total {item['name']}.eps",
                        bbox_inches='tight')
            plt.show()

    # def total_energy_consumption_all_old(self):
    #     count = -1
    #     space = [' ', '  ', '   ']
    #     # Cria 3 subplots lado a lado
    #     fig, axes = plt.subplots(1, 3, figsize=(
    #         24, 5), constrained_layout=True, gridspec_kw={'wspace': 0.1})

    #     for idx, item in enumerate(self.dfs):
    #         ax = axes[idx]  # Seleciona o eixo correspondente
    #         df = item['df']
    #         count += 1
    #         experiment_names = []
    #         total_energies = []

    #         for label in df:
    #             if 'energy_consumption' in label:
    #                 experiment_names.append(
    #                     f"{space[count]}{label.replace('_energy_consumption', '').replace('sta', 'sensor ')}"
    #                 )
    #                 total_energies.append(df[label].sum())

    #         bars = ax.bar(
    #             experiment_names,
    #             total_energies,
    #             color='skyblue',
    #             edgecolor='black',
    #             label=item['name']
    #         )
    #         # Adiciona os valores no topo das barras
    #         for bar, energy in zip(bars, total_energies):
    #             ax.text(
    #                 bar.get_x() + bar.get_width() / 2,  # Posição X
    #                 bar.get_height(),                   # Posição Y
    #                 f'{energy:.2f}',                    # Texto formatado
    #                 ha='center', va='bottom', fontsize=10
    #             )

    #         ax.set_xlabel('Sensores', fontsize=14)
    #         ax.set_ylabel('Energia Consumida (Wh)', fontsize=14)
    #         ax.set_title(f'Consumo Total - {item["name"]}', fontsize=16)
    #         ax.tick_params(axis='x', rotation=90, labelsize=10)
    #         ax.tick_params(axis='y', labelsize=10)
    #         # ax.legend(title="Clientes", fontsize=10, title_fontsize=12)

    #     fig.suptitle('Consumo Total de Energia por Experimento',
    #                  fontsize=20)  # Título geral

    #     plt.savefig("consumo_total_todos_experimentos.eps",
    #                 bbox_inches='tight')
    #     plt.show()

    # def total_energy_consumption_all(self):

    #     for item in self.dfs:
    #         df = item['df']
    #         experiment_names = []
    #         total_energies = []
    #         for label in df:
    #             if 'energy_consumption' in label:

    #                 experiment_names.append(
    #                     f"{label.replace('_energy_consumption','').replace('sta','- sensor ')}")
    #                 total_energies.append(df[label].sum())

    #         # Cria o gráfico de barras
    #         # plt.figure(figsize=(10, 6))
    #         plt.figure(figsize=(18, 10))
    #         bars = plt.bar(experiment_names, total_energies,
    #                        color='skyblue', edgecolor='black')

    #         plt.xlabel('Experimento', fontsize=18)
    #         plt.ylabel('Energia Consumida (Wh)', fontsize=18)
    #         plt.title(
    #             f"Consumo Total de Energia no experimento {item['name']}", fontsize=20)
    #         # plt.xticks(fontsize=14)
    #         plt.xticks(rotation=90, fontsize=14)  # Rotaciona 45 graus

    #         plt.yticks(fontsize=14)

    #         # Adiciona os valores no topo das barras
    #         for bar, energy in zip(bars, total_energies):
    #             plt.text(bar.get_x() + bar.get_width() / 2,  # Posição X
    #                      bar.get_height(),                   # Posição Y
    #                      f'{energy:.2f}',                    # Texto formatado
    #                      ha='center', va='bottom', fontsize=12)

    #         plt.tight_layout()
    #         # plt.show()
    #         plt.savefig(f"consumo cada cliente {item['name']}.eps",
    #                     bbox_inches='tight')

    def mean_acc_k_folds(self):
        plt.figure(figsize=(10, 6))
        possible_colors = ['blue', 'green', 'red', 'purple', 'orange']
        experiments = {}

        for item in self.dfs:
            df = item['df']
            if (item['experiment'] in experiments) is False:
                experiments[item['experiment']] = []

            experiments[item['experiment']].append(df['mean_accuracy'])

        for idx, experiment in reversed(list(enumerate(experiments.__reversed__()))):
            experiments_matrix = experiments[experiment]

            max_tamanho = max(len(line) for line in experiments_matrix)

            acc = np.zeros(max_tamanho)
            acc_qtd = np.zeros(max_tamanho)
            mean = np.zeros(max_tamanho)
            error = np.zeros(max_tamanho)
            error_qtd = np.zeros(max_tamanho)
            std_d = np.zeros(max_tamanho)

            for i in range(max_tamanho):
                for line in experiments_matrix:
                    if len(line) > i:
                        acc[i] += line[i]
                        acc_qtd[i] += 1

            # print(acc)
            # print(acc_qtd)
            for i in range(max_tamanho):
                mean[i] = acc[i] / acc_qtd[i]

            for i in range(max_tamanho):
                for line in experiments_matrix:
                    if len(line) > i:
                        error[i] += (line[i] - mean[i])**2
                        error_qtd[i] += 1

            for i in range(max_tamanho):
                if (error_qtd[i] - 1.0) > 0:
                    std_d[i] = math.sqrt(error[i] / (error_qtd[i] - 1.0))

            # plt.figure(figsize=(10, 6))
            # plt.fill_between(range(max_tamanho), mean -
            #                  std_d, mean+std_d, alpha=.3, color=possible_colors[idx % len(possible_colors)])
            plt.fill_between(range(max_tamanho), mean -
                             std_d, mean+std_d, alpha=.3)
            # plt.plot(range(max_tamanho), mean,
            #          label=f"{experiment}", color=possible_colors[idx % len(possible_colors)])
            plt.plot(range(max_tamanho), mean,
                     label=f"{experiment}")

            plt.xlabel('Round', fontsize=18)
            plt.ylabel('Accuracy', fontsize=18)
            plt.title('Mean accuracy in K-folds with standard deviation')
            plt.legend(fontsize=16)
            plt.tick_params(labelsize=16)
        plt.savefig(f"experiments_out/{'out'}.pdf")
        # plt.show()
