
import os
import socket
import paho.mqtt.client as paho


#Get environment variables
MY_NAME = socket.gethostname()
BROKER = os.environ.get('BROKER_HOSTNAME')
NUM_OF_AGENTS= int(os.environ.get('AGENTS_NUMBER'))

my_number = int(MY_NAME[-1])
num_of_mates = NUM_OF_AGENTS -1
my_mates = [(my_number + i)%3 for i in range(1, num_of_mates + 1)]

print(f"My name is {MY_NAME}, Broker: {BROKER}, Number of agents: {NUM_OF_AGENTS}")

def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed to topic")

def on_message(client, userdata, msg):
    print(f"From topic: {msg.topic} | msg: {msg.payload}")  

client = paho.Client()
client.on_subscribe = on_subscribe
client.on_message = on_message
client.connect(BROKER, 1883)

# Subscribe for related topics
client.subscribe(f"{MY_NAME}/#", qos=1)

# Send hello to all agents
print(f"Sending hello to agents {my_mates}")
for mate in my_mates:
    client.publish(f"agent-{mate}/hello", f"Hello from agent-{my_number}!", qos=1)

client.loop_forever()