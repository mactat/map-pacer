
import os
import socket
import paho.mqtt.client as mqtt
import sys


#Get environment variables
MY_NAME = socket.gethostname()
BROKER = os.environ.get('BROKER_HOSTNAME')
BROKER_PORT = int(os.environ.get('BROKER_PORT'))
BROKER_CLOUD = os.environ.get('CLOUD_BROKER_HOSTNAME')
BROKER_CLOUD_PORT = int(os.environ.get('CLOUD_BROKER_PORT'))
NUM_OF_AGENTS= int(os.environ.get('AGENTS_NUMBER'))

my_number = int(MY_NAME[-1])
num_of_mates = NUM_OF_AGENTS -1
my_mates = [(my_number + i)%3 for i in range(1, num_of_mates + 1)]

print(f"My name is {MY_NAME}, Broker: {BROKER}, Number of agents: {NUM_OF_AGENTS}")

def on_subscribe(client_local, userdata, mid, granted_qos):
    print("Subscribed to topic")

def on_message(client_local, userdata, msg):
    print(f"From topic: {msg.topic} | msg: {msg.payload}")  

client_local = mqtt.Client()
client_local.username_pw_set(username="agent", password="agent-pass")
client_local.on_subscribe = on_subscribe
client_local.on_message = on_message
client_local.connect(BROKER, BROKER_PORT)

client_cloud = mqtt.Client()
client_cloud.username_pw_set(username="agent", password="agent-pass")
client_cloud.on_subscribe = on_subscribe
client_cloud.on_message = on_message
client_cloud.connect(BROKER_CLOUD, BROKER_CLOUD_PORT)

# Subscribe for related topics
client_local.subscribe(f"{MY_NAME}/#", qos=1)
client_cloud.subscribe(f"{MY_NAME}/#", qos=1)

# Send hello to all agents
print(f"Sending hello to agents {my_mates}")
for mate in my_mates:
    client_local.publish(f"agent-{mate}/hello", f"Hello from agent-{my_number}!", qos=2)

print(f"Sending hello to cloud-agent")
client_cloud.publish(f"cloud-agent/hello", f"Hello from agent-{my_number}!", qos=2)

while 1:
    client_local.loop(0.01)
    client_cloud.loop(0.01)
