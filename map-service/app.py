
import os
import socket
import paho.mqtt.client as mqtt
import sys
import random
import json
import numpy as np
from log_lib import get_default_logger


#Get environment variables
MY_NAME = socket.gethostname()
BROKER = os.environ.get('BROKER_HOSTNAME')
BROKER_PORT = int(os.environ.get('BROKER_PORT'))
BROKER_CLOUD = os.environ.get('CLOUD_BROKER_HOSTNAME')
BROKER_CLOUD_PORT = int(os.environ.get('CLOUD_BROKER_PORT'))
NUM_OF_AGENTS= int(os.environ.get('AGENTS_NUMBER'))
agents = []
map_id = 0
current_map = []

logger = get_default_logger(MY_NAME)
logger.info(f"My name is {MY_NAME}, Broker: {BROKER}")

def generate_map(map_size):
    global current_map
    current_map.clear()
    for x in range(map_size):
        current_map.append(np.random.choice([0,1],map_size,p=[0.8,0.2]).tolist())
    # inject agents to a map
    for agent in agents:
        x_start = random.randint(0, map_size - 1)
        y_start = random.randint(0, map_size - 1)
        x_end = random.randint(0, map_size - 1)
        y_end = random.randint(0, map_size - 1)

        current_map[x_start][y_start] = f"{agent}-start"
        current_map[x_end][y_end] = f"{agent}-end"
    logger.info(current_map)

def announce_new_map():
    logger.info("Announcing new map")
    # map to json
    map_json = json.dumps(current_map)
    client_local.publish("agents/map/new", map_json, qos=2)

def on_subscribe(client_local, userdata, mid, granted_qos):
    logger.info("Subscribed to topic")

def on_message(client_local, userdata, msg):
    msg_str = msg.payload.decode()
    match msg.topic:
        case "map-service/hello":
            logger.debug(f"Hello from {msg_str}")
            if msg_str not in agents:
                agents.append(msg_str)
                logger.info(f"Agents: {agents}")

        case "map-service/new-map":
            logger.info("Generating new map")
            generate_map(int(msg_str))
            announce_new_map()

        case _:
            logger.info("Unknown topic")
            logger.info(f"From topic: {msg.topic} | msg: {msg_str}")

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
client_local.subscribe(f"map-service/#", qos=2)
client_cloud.subscribe(f"map-service/#", qos=2)

# Restart discovery of agents
client_local.publish("agents/discovery/start","It's map-service looking for ya" , qos=2)

while 1:
    client_local.loop(0.01)
    client_cloud.loop(0.01)
