import subprocess
import os


class ExtBroker:
    def __init__(self):
        self.process = None

    def run_ext_brk(self):
        command = (
            "sudo docker run --name ext_brk -it "
            "-p 1883:1883 -p 9001:9001 "
            "-v ./mosquitto/mosquitto.conf:/mosquitto/config/mosquitto.conf "
            "eclipse-mosquitto"
        )

        try:
            # Executa o comando em um novo terminal usando xterm
            self.process = subprocess.Popen(
                ["xterm", "-e", f"{command}; exec bash"],
                preexec_fn=os.setpgrp)
            print(
                "O container do broker externo está rodando em uma nova janela de xterm.")
        except subprocess.CalledProcessError as e:
            print(f"Erro ao executar o comando: {e}")

    def stop_ext_brk(self):
        print("\nEncerrando o container Docker do broker...")
        if hasattr(self, 'process'):
            # Primeiro, para o container
            subprocess.run("sudo docker stop ext_brk", shell=True)
            # Em seguida, remove o container
            subprocess.run("sudo docker rm ext_brk", shell=True)
            # Por fim, encerra o processo do terminal xterm
            self.process.terminate()
        else:
            print("Nenhum container do broker em execução para encerrar.")


if __name__ == "__main__":
    e = ExtBroker()
    e.run_ext_brk()
