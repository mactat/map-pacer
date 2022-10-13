
import copy
import os, random
import socket
import paho.mqtt.client as mqtt
import sys
import random
import json
import numpy as np
from libs.log_lib import get_default_logger
from libs.algo_lib_3d import Grid_map as Grid_map_3d
from prometheus_client import start_http_server, Summary, Enum

#Get environment variables
MY_NAME = socket.gethostname()
BROKER_CLOUD = os.environ.get('CLOUD_BROKER_HOSTNAME')
BROKER_CLOUD_PORT = int(os.environ.get('CLOUD_BROKER_PORT'))
agents = []
coords = []
map_id = 0
current_map = []

logger = get_default_logger(MY_NAME)
logger.info(f"My name is {MY_NAME}, Broker: {BROKER_CLOUD}")

# Metrics
monitoring_setup_map_time = Summary('setup_map_time', 'Time spent for map setup')
monitoring_calculate_path_time = Summary('calculate_path_time', 'Time spent for path calculation')
start_http_server(8080)


@monitoring_calculate_path_time.time()
def calculate_a_star(grid_map, start, end):
    possible, path = grid_map.a_star(start, end)
    return possible, path

@monitoring_setup_map_time.time()
def setup_map(current_map):
    temp_map = copy.deepcopy(current_map)
    grid_map = Grid_map_3d(mode="no_diag", mark_path=True)
    grid_map.load_from_list(temp_map)
    return grid_map

def calculate_sequence(algo="CA_star"):
    logger.info("I will calculate all paths.")
    grid_map = setup_map(current_map)
    for agent, (start, end) in zip(agents, coords):
        if not start or not end:
            logger.warning(f"Start or end not found")
            client_cloud.publish("backend/path", json.dumps({"agent": agent, "path": "not found"}), qos=2)
            possible = False
        else:
            possible, path = calculate_a_star(grid_map, start, end)
        if possible:
            logger.info(f"Path found: {path}")
            client_cloud.publish("backend/path", json.dumps({"agent": agent, "path": [(x, y) for x,y,_ in path]}), qos=2)
        else:
            logger.info(f"Path not found")
            client_cloud.publish("backend/path", json.dumps({"agent": agent, "path": "not found"}), qos=2)

def extract_coords(new_map):
    coords = []
    start, end = None, None
    for agent in agents:
        for i, row in enumerate(new_map):
            for j, cell in enumerate(row):
                if cell == f"{agent}-start": 
                        start = (i,j)
                        new_map[i][j] = 0
                elif cell == f"{agent}-end":
                        end = (i,j)
                        new_map[i][j] = 0
        coords.append((start, end))
    return new_map, coords

def adopt_new_map(new_map):
    global current_map, coords
    current_map, coords = extract_coords(new_map)
    logger.info(f"New map. Coords: {coords}, Agents: {agents}")

# Form mqtt
def on_subscribe(client_local, userdata, mid, granted_qos):
    logger.info("Subscribed to topic")

def on_message(client_local, userdata, msg):
    msg_str = msg.payload.decode()
    match msg.topic:
        case "cloud-agent/hello":
            logger.debug(f"Hello from {msg_str}")
            if msg_str not in agents:
                agents.append(msg_str)
                logger.info(f"Agents: {agents}")

        case "cloud-agent/map/new":
            # map from json
            new_map = json.loads(msg_str)
            adopt_new_map(new_map)
        case "cloud-agent/calculate/sequence_mode":
            data = json.loads(msg_str)
            calculate_sequence(algo="CA_star")
        case _:
            logger.info("Unknown topic")
            logger.info(f"From topic: {msg.topic} | msg: {msg_str}")


client_cloud = mqtt.Client()
client_cloud.username_pw_set(username="agent", password="agent-pass")
client_cloud.on_subscribe = on_subscribe
client_cloud.on_message = on_message
client_cloud.connect(BROKER_CLOUD, BROKER_CLOUD_PORT)

# Subscribe for related topics
client_cloud.subscribe(f"cloud-agent/#", qos=2)

# Restart discovery of agents
client_cloud.publish("agents/discovery/start","It's cloud-agent looking for ya" , qos=2)
client_cloud.publish("map-service/re-announce-map","It's cloud-agent looking for ya" , qos=2)

while 1:
    client_cloud.loop(0.01)
