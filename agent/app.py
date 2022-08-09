
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
    print("Subscribed: "+str(mid)+" "+str(granted_qos))

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))    

client = paho.Client()
client.on_subscribe = on_subscribe
client.on_message = on_message
client.connect(BROKER, 1883)
client.subscribe(f"{MY_NAME}/#", qos=1)

# Send hello
for mate in my_mates:
    client.publish("agent-statefullset-"+str(mate), f"Hello agent-{mate} from agent-{my_number}", qos=1)

client.loop_forever()