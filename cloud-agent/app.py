
import copy
import os
import random
import socket
import paho.mqtt.client as mqtt
import sys
import random
import json
import numpy as np
from libs.log_lib import get_default_logger
from libs.algo_lib_3d import Grid_map as Grid_map_3d
from libs.algo_lib import Grid_map
from prometheus_client import start_http_server, Summary, Enum

# Get environment variables
MY_NAME = socket.gethostname()
BROKER_CLOUD = os.environ.get('CLOUD_BROKER_HOSTNAME')
BROKER_CLOUD_PORT = int(os.environ.get('CLOUD_BROKER_PORT'))

logger = get_default_logger(MY_NAME)
logger.info(f"My name is {MY_NAME}, Broker: {BROKER_CLOUD}")

# Metrics
monitoring_setup_map_time = Summary(
    'setup_map_time', 'Time spent for map setup')
monitoring_calculate_path_time = Summary(
    'calculate_path_time', 'Time spent for path calculation')
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


def calculate_single(new_map, agents, system_id, start_time, algo="A*"):
    current_map, coords = extract_coords(new_map, agents)
    temp_map = copy.deepcopy(current_map)
    grid_map = Grid_map(mode="no_diag")
    grid_map.load_from_list(temp_map)
    for agent, (start, end) in zip(agents, coords):
        possible = False
        if not start or not end:
            logger.warning(f"Start or end not found")
            client_cloud.publish(f"{system_id}/{agent}/path", json.dumps(
                {"agent": agent, "path": "not found", "system_id": system_id}), qos=0)
        else:
            possible, path = grid_map.find_path(start, end, algo=algo)
        if possible:
            # to be changed to dynamic
            full_path = path + [path[-1]*(100-len(path))]
            logger.info(f"Path found: {path}")
            client_cloud.publish(f"{system_id}/{agent}/path", json.dumps(
                {"agent": agent, "path": full_path, "system_id": system_id, "start_time": start_time}), qos=0)
        else:
            logger.info(f"Path not found")
            client_cloud.publish(f"{system_id}/{agent}/path", json.dumps(
                {"agent": agent, "path": "not found", "system_id": system_id, "start_time": start_time}), qos=0)


def calculate_sequence(new_map, agents, system_id, start_time, algo="CA_star"):
    logger.info(
        f"I will calculate all paths fo agents {agents} system: {system_id}")
    current_map, coords = extract_coords(new_map, agents)
    grid_map = setup_map(current_map)
    for agent, (start, end) in zip(agents, coords):
        possible = False
        if not start or not end:
            logger.warning(f"Start or end not found")
            client_cloud.publish(f"{system_id}/{agent}/path", json.dumps(
                {"agent": agent, "path": "not found", "system_id": system_id, "start_time": start_time}), qos=0)
        else:
            possible, path = calculate_a_star(grid_map, start, end)
        if possible:
            logger.info(f"Path found: {path}")
            client_cloud.publish(f"{system_id}/{agent}/path", json.dumps(
                {"agent": agent, "path": [(x, y) for x, y, _ in path], "system_id": system_id, "start_time": start_time}), qos=0)
        else:
            logger.info(f"Path not found")
            client_cloud.publish(f"{system_id}/{agent}/path", json.dumps(
                {"agent": agent, "path": "not found", "system_id": system_id, "start_time": start_time}), qos=0)


def extract_coords(new_map, agents):
    coords = []
    start, end = None, None
    for agent in agents:
        for i, row in enumerate(new_map):
            for j, cell in enumerate(row):
                if cell == f"{agent}-start":
                    start = (i, j)
                    new_map[i][j] = 0
                elif cell == f"{agent}-end":
                    end = (i, j)
                    new_map[i][j] = 0
        coords.append((start, end))
    return new_map, coords

# Form mqtt


def on_subscribe(client_local, userdata, mid, granted_qos):
    logger.info("Subscribed to topic")


def on_message(client_local, userdata, msg):
    msg_str = msg.payload.decode()
    match msg.topic:
        case "cloud-agent/calculate/sequence_mode":
            data = json.loads(msg_str)
            calculate_sequence(data["map"], data["agents"], data["system_id"],
                               start_time=data["start_time"], algo="CA_star")
        case "cloud-agent/calculate/single_mode":
            data = json.loads(msg_str)
            calculate_single(data["map"], data["agents"], data["system_id"],
                             start_time=data["start_time"], algo=data["algo"])
        case _:
            logger.info("Unknown topic")
            logger.info(f"From topic: {msg.topic} | msg: {msg_str}")


client_cloud = mqtt.Client(client_id=MY_NAME, clean_session=False)
client_cloud.username_pw_set(username="agent", password="agent-pass")
client_cloud.on_subscribe = on_subscribe
client_cloud.on_message = on_message
client_cloud.connect(BROKER_CLOUD, BROKER_CLOUD_PORT)

# Subscribe for related topics
client_cloud.subscribe(f"cloud-agent/#", qos=0)


while 1:
    client_cloud.loop(0.01)
