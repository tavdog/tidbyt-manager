import paho.mqtt.client as mqtt
import sys
# set server and port to the first two arguments
server = sys.argv[1]
port = int(sys.argv[2])

client = mqtt.Client()
# connect to the server
try:
    code = client.connect(server, port, 60)
    if code == 0:
        print(f"Connection to {server} on port {port} sucessful")
    else:
        print(f"result code was {code}")
except Exception as e:
    print(f"excepetion occured {e}")


