import sys
import numpy as np
import torch

from .fedavg import FedAvg
from .fedsketch import FedSketchAgg

from Pyfhel import Pyfhel, PyCtxt


def salvar_matriz_binaria(matriz, nome_arquivo):
    """
    Salva a matriz binária em um arquivo especificado, incluindo as chaves de linha, coluna e valor e considerando tamanhos variáveis de valores.

    Argumentos:
      matriz: A matriz a ser salva (dicionário de dicionários).
      nome_arquivo: O nome do arquivo binário para salvar a matriz.
    """
    with open(nome_arquivo, 'wb') as f:

        # Percorrer cada elemento da matriz
        for linha1 in matriz:
            # Converter a chave linha1 em bytes
            bytes_linha1 = linha1.encode('utf-8')

            for coluna1 in matriz[linha1]:

                # Converter a chave linha1 em bytes
                bytes_coluna1 = coluna1.encode('utf-8')

                # Escrever o tamanho da chave linha1 e os bytes da chave no arquivo
                f.write(len(bytes_linha1).to_bytes(4, 'big'))
                f.write(bytes_linha1)
                # Escrever o tamanho da chave linha1 e os bytes da chave no arquivo
                f.write(len(bytes_coluna1).to_bytes(4, 'big'))
                f.write(bytes_coluna1)

                # Obter o valor (PyCtxt)
                valor_pyctxt = matriz[linha1][coluna1]
                # print(matriz, file=sys.stderr)
                bytes_pyctxt = valor_pyctxt.to_bytes()

                # Converter o tamanho do valor em bytes
                tamanho_valor = len(bytes_pyctxt).to_bytes(4, 'big')

                # Escrever o tamanho do valor no arquivo
                f.write(tamanho_valor)

                # escrever no arquivo
                f.write(bytes_pyctxt)
        f.close()


def cka_unecrypted(X, Y, XTX, YTY):
  # Implements linear CKA as in Kornblith et al. (2019)
    X = X.copy()
    Y = Y.copy()
    YTX = Y.T.dot(X)
    return (YTX ** 2).sum() * XTX * YTY


def cka_encrypted(X, Y, XTX, YTY, HE):
    X = X.copy()
    Y = Y.copy()
    if len(X) == len(Y) == 1:
        YTX = X[0] @ Y[0]
    else:
        YTX = [~(X[i]*Y[i]) for i in range(len(X[i]))]
        for i in range(1, len(YTX)):
            YTX[0] += YTX[i]
        YTX = HE.cumul_add(YTX[0])
    HE.rescale_to_next(YTX)
    bottom = XTX * YTY
    HE.relinearize(bottom)
    square = YTX * YTX
    HE.relinearize(square)
    top = HE.cumul_add(square, False, 1)
    HE.relinearize(top)
    result = top * bottom
    HE.relinearize(result)
    return result


def decode_value(HE, value):
    return PyCtxt(pyfhel=HE, bytestring=value.encode('cp437'))


def decode_array(HE, encrypted_array):
    out = []
    for element in encrypted_array:
        b = element.encode('cp437')
        c_res = PyCtxt(pyfhel=HE, bytestring=b)
        out.append(c_res)
    return out


def encrypt_array(HE_f, array):
    CASE_SELECTOR = 1          # 1 or 2

    case_params = {
        1: {'l': 256},         # small l
        2: {'l': 65536},       # large l
    }[CASE_SELECTOR]
    l = case_params['l']

    return [HE_f.encrypt(array[j:j+HE_f.get_nSlots()]) for j in range(0, l, HE_f.get_nSlots())]


def encrypt_value(HE_f, value):
    return HE_f.encrypt(value)


def cka(X, Y, XTX, YTY, HE=None, crypt=False):
    if crypt:
        X = decode_array(HE, X)
        Y = decode_array(HE, Y)
        XTX = decode_value(HE, XTX)
        YTY = decode_value(HE, YTY)
        res = cka_encrypted(X, Y, XTX, YTY, HE)
    else:
        res = cka_unecrypted(np.array(X), np.array(Y), XTX, YTY)
    return res


class Ckksfed:

    def __init__(self):
        self.distance_matrix = None
        self.fedsketch = True
        dir_path = "temp/ckksfed_fhe/pasta"
        self.HE_f = Pyfhel()  # Empty creation
        self.HE_f.load_context(dir_path + "/context")
        self.HE_f.load_public_key(dir_path + "/pub.key")
        self.HE_f.load_relin_key(dir_path + "/relin.key")
        self.HE_f.load_rotate_key(dir_path + "/rotate.key")

    def get_distance_matrix(self, client_training_responses, ENCRYPT):
        distance_matrix = {}
        for client_i in client_training_responses:
            client_distance = {}
            for client_j in client_training_responses:
                client_distance[client_j] = cka(client_training_responses[client_i]["training_args"][0],
                                                client_training_responses[client_j]["training_args"][1],
                                                client_training_responses[client_i]["training_args"][2],
                                                client_training_responses[client_j]["training_args"][2],
                                                self.HE_f, crypt=ENCRYPT)
            distance_matrix[client_i] = client_distance
        return distance_matrix

    def aggregate(self, client_training_responses, trainers_list):
        print("Aggregation process initiated")

        ENCRYPTED = client_training_responses[trainers_list[0]
                                              ]["training_args"][4]

        print("Calculating the distance matrix")
        self.distance_matrix = self.get_distance_matrix(
            client_training_responses, ENCRYPT=ENCRYPTED)


        if not self.fedsketch:
            print("FedAvg selected")
            fed_avg = FedAvg()
        else:
            print("FedSketchAgg selected")
            fed_avg = FedSketchAgg()

        weights_dict = {}
        if len(client_training_responses[trainers_list[0]]["training_args"][3]) == 0:
            print("No cluster provided (first round) => Aggregating all weights")
            weights = fed_avg.aggregate(client_training_responses)
            weights_dict = {c: weights for c in trainers_list}
        else:
            print("Aggregating each cluster")
            aggregated_clusters = set()
            for client_i in trainers_list:
                cluster = client_training_responses[client_i]["training_args"][3]

                if tuple(cluster) in aggregated_clusters:
                    continue

                print("Aggregating:")
                print(cluster)

                aggregated_clusters.add(tuple(cluster))
                weights = fed_avg.aggregate(
                    {c: client_training_responses[c] for c in cluster})
                weights_dict = weights_dict | {c: weights for c in cluster}

        agg_response = {}
        for client in trainers_list:
            agg_response[client] = {"weights": weights_dict[client]}

        if ENCRYPTED:
            print("Saving encrypted matrix in external file")
            salvar_matriz_binaria(
                self.distance_matrix, 'data_temp/data.bin')
        else:
            print("Saving unencrypted matrix")
            agg_response['all'] = {
                "distances": self.distance_matrix, "clients": trainers_list}
        return agg_response
