import shutil
import os


def read_energy():
    """
    Lê um valor float de um arquivo.

    :param file_path: Caminho para o arquivo.
    :return: Valor float lido ou None se houver erro.
    """

    # Caminho do arquivo de energia
    file_path = "../tmp/consumption"

    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(
                f"O arquivo {file_path} não foi encontrado.")

        with open(file_path, 'r') as file:
            content = file.read().strip()

        # Tenta converter o valor para float
        value = float(content)
        return value
    except ValueError:
        print(f"Erro: O valor no arquivo {file_path} não é um float válido.")
    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(f"Erro inesperado: {e}")
    return None


def copiar_arquivo(origem, destino):
    """
    Copia um arquivo de um local para outro.

    Parâmetros:
        origem (str): Caminho completo do arquivo de origem.
        destino (str): Caminho completo do arquivo de destino.

    Retorna:
        bool: True se a cópia foi bem-sucedida, False caso contrário.
    """
    try:
        # Verifica se o arquivo de origem existe
        if not os.path.isfile(origem):
            print(f"Arquivo de origem não encontrado: {origem}")
            return False

        # Garante que o diretório de destino exista
        os.makedirs(os.path.dirname(destino), exist_ok=True)

        # Copia o arquivo
        shutil.copy2(origem, destino)
        print(f"Arquivo copiado com sucesso de {origem} para {destino}")
        return True
    except Exception as e:
        print(f"Erro ao copiar o arquivo: {e}")
        return False
