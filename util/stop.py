import paho.mqtt.client as mqtt
import sys
import time

n = len(sys.argv)
if (n != 2):
    print("Correct use: python stop.py <broker_address>")
    sys.exit(1)


class Color:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD_START = '\033[1m'
    BOLD_END = '\033[0m'
    RESET = "\x1B[0m"


BROKER_ADDR = sys.argv[1]


# Callback when the client receives a CONNECT response from the server.
def on_connect(client, userdata, flags, rc):
    client.subscribe('minifed/stopQueue')
    client.subscribe('minifed/autoWaitContinue')
    # print(Color.YELLOW + "Subscribed to topics." + Color.RESET)


def on_message_stop(client, userdata, message):
    print(Color.RED + "Received message to stop!" + Color.RESET)
    cleanup_and_exit(client)


def on_message_continue(client, userdata, message):
    print(Color.GREEN + "Received message to continue!" + Color.RESET)
    cleanup_and_exit(client)


def cleanup_and_exit(client):
    client.disconnect()


client = mqtt.Client('auto_stop')
client.on_connect = on_connect
client.message_callback_add('minifed/stopQueue', on_message_stop)
client.message_callback_add('minifed/autoWaitContinue', on_message_continue)

try:
    client.connect(BROKER_ADDR, bind_port=1883,
                   keepalive=0)
    print(Color.YELLOW + "Waiting for messages..." + Color.RESET)
    client.loop_forever()  # Start network loop
except KeyboardInterrupt:
    print("\n" + Color.BLUE + "Interrupted by user." + Color.RESET)
    cleanup_and_exit(client)
except Exception as e:
    print(Color.RED + f"An error occurred: {e}" + Color.RESET)
    time.sleep(200)
    cleanup_and_exit(client)
