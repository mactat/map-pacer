
import os, random
import socket
import paho.mqtt.client as mqtt
import sys
import random
import json
import numpy as np
from libs.log_lib import get_default_logger
import ssl


#Get environment variables
MY_NAME = socket.gethostname()
BROKER = os.environ.get('BROKER_HOSTNAME')
BROKER_PORT = int(os.environ.get('BROKER_PORT'))
BROKER_CLOUD = os.environ.get('CLOUD_BROKER_HOSTNAME')
BROKER_CLOUD_PORT = int(os.environ.get('CLOUD_BROKER_PORT'))
NUM_OF_AGENTS= int(os.environ.get('AGENTS_NUMBER'))
SYSTEM_ID = os.environ.get('SYSTEM_ID')
agents = []
map_id = 0
current_map = []

logger = get_default_logger(MY_NAME)
logger.info(f"My name is {MY_NAME}, System ID:{SYSTEM_ID},  Broker: {BROKER}")


def adopt_new_map(new_map):
    global current_map
    current_map = new_map
    logger.info("Map adopted")

def generate_map(map_size):
    global current_map
    current_map.clear()
    for x in range(map_size):
        current_map.append(np.random.choice([0,1],map_size,p=[0.8,0.2]).tolist())
    put_agents_in_map()
    logger.info("Random map generated")

def get_map_from_file(map_file="random"):
    global current_map
    if "random" in map_file: map_file = random.choice(os.listdir("./maps"))

    # take map from text file a cast to int
    with open(f"./maps/{map_file}") as f:
        current_map = [[int(num) for num in line.split()] for line in f]
    put_agents_in_map()
    logger.info(f"Map from file: {map_file} generated")

# Reschedule position of the agent
def get_new_position(agent_name):
    pass

def get_random_free_position(my_map, num_of_agents):
    positions = []
    while len(positions) < num_of_agents:
        x = random.randint(0, len(my_map) - 1)
        y = random.randint(0, len(my_map) - 1)
        if my_map[x][y] == 0:
            positions.append([x, y])
    return positions

# Have to be smarter to avoid spawning in the wall
def put_agents_in_map():
    global current_map, agents
    # inject agents to a map
    for agent, position in zip(agents, get_random_free_position(current_map, len(agents))):
        current_map[position[0]][position[1]] = f"{agent}-start"
    for agent, position in zip(agents, get_random_free_position(current_map, len(agents))):
        current_map[position[0]][position[1]] = f"{agent}-end"


def announce_new_map():
    logger.info("Announcing new map")
    # map to json
    map_json = json.dumps(current_map)
    client_local.publish(f"{SYSTEM_ID}/agents/map/new", map_json, qos=2)
    client_cloud.publish("cloud-agent/map/new", map_json, qos=2)

def on_subscribe(client_local, userdata, mid, granted_qos):
    logger.info("Subscribed to topic")

def on_message(client_local, userdata, msg):
    msg_str = msg.payload.decode()
    if msg.topic == f"{SYSTEM_ID}/map-service/hello":
        logger.debug(f"Hello from {msg_str}")
        if msg_str not in agents:
            agents.append(msg_str)
            logger.info(f"Agents: {agents}")

    elif msg.topic == f"{SYSTEM_ID}/map-service/random-map":
        logger.info("Generating new map")
        generate_map(int(msg_str))
        announce_new_map()

    elif msg.topic == f"{SYSTEM_ID}/map-service/re-announce-map":
        logger.info("Re-announcing map")
        announce_new_map()
    elif msg.topic == f"{SYSTEM_ID}/map-service/map-from-file":
        get_map_from_file(map_file=msg_str)
        announce_new_map()
    elif msg.topic == f"{SYSTEM_ID}/map-service/adopt-map":
        new_map = json.loads(msg_str)
        adopt_new_map(new_map)
        announce_new_map()

    else:
        logger.info("Unknown topic")
        logger.info(f"From topic: {msg.topic} | msg: {msg_str}")

client_local = mqtt.Client(client_id=MY_NAME, clean_session=False)
client_local.username_pw_set(username="agent", password="agent-pass")
client_local.on_subscribe = on_subscribe
client_local.on_message = on_message
client_local.connect(BROKER, BROKER_PORT)

client_cloud = mqtt.Client(client_id=MY_NAME, transport='websockets', clean_session=False)
client_cloud.ws_set_options(path="/mqtt", headers=None)

##### COMMENT TO RUN WITH TILT TODO: fix it
client_cloud.tls_set(tls_version=2, cert_reqs=ssl.CERT_NONE)
client_cloud.tls_insecure_set(True)
#####

client_cloud.username_pw_set(username="agent", password="agent-pass")
client_cloud.on_subscribe = on_subscribe
client_cloud.on_message = on_message
client_cloud.connect(BROKER_CLOUD, BROKER_CLOUD_PORT)

# Subscribe for related topics
client_local.subscribe(f"{SYSTEM_ID}/map-service/#", qos=2)
client_cloud.subscribe(f"{SYSTEM_ID}/map-service/#", qos=2)

# Restart discovery of agents
client_local.publish(f"{SYSTEM_ID}/agents/discovery/start","It's map-service looking for ya" , qos=2)

while 1:
    client_local.loop(0.01)
    client_cloud.loop(0.01)
