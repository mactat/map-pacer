
import os, random
import socket
import paho.mqtt.client as mqtt
import sys
import random
import json
import numpy as np
from libs.log_lib import get_default_logger
from prometheus_client import start_http_server, Summary, Enum

#Get environment variables
MY_NAME = socket.gethostname()
BROKER_CLOUD = os.environ.get('CLOUD_BROKER_HOSTNAME')
BROKER_CLOUD_PORT = int(os.environ.get('CLOUD_BROKER_PORT'))
agents = []
map_id = 0
current_map = []

logger = get_default_logger(MY_NAME)
logger.info(f"My name is {MY_NAME}, Broker: {BROKER_CLOUD}")

# Metrics
monitoring_setup_map_time = Summary('setup_map_time', 'Time spent for map setup')
monitoring_calculate_path_time = Summary('calculate_path_time', 'Time spent for path calculation')

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

while 1:
    client_cloud.loop(0.01)
