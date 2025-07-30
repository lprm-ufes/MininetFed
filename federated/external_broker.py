import subprocess
import os


class ExtBroker:
    def __init__(self):
        self.process = None

    def run_ext_brk(self):
        command = (
            "sudo docker run --name ext_brk -it "
            "-p 1883:1883 -p 9001:9001 "
            "-v ./mosquitto/mosquitto.conf:/etc/config/mosquitto.conf "
            "eclipse-mosquitto"
        )

        try:
            self.process = subprocess.Popen(
                ["xterm", "-e", f"{command}; exec bash"],
                preexec_fn=os.setpgrp)
        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")

    def stop_ext_brk(self):
        print("\nShutting down the broker's Docker container...")
        if hasattr(self, 'process'):
            subprocess.run("sudo docker stop ext_brk", shell=True)
            subprocess.run("sudo docker rm ext_brk", shell=True)
            self.process.terminate()
        else:
            print("No broker containers running to terminate.")


if __name__ == "__main__":
    e = ExtBroker()
    e.run_ext_brk()
