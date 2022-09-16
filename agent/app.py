
import copy
import os
import socket
import paho.mqtt.client as mqtt
import sys
import random, time
import json
from algo_lib import Grid_map, Obstacle, Cell
from log_lib import get_default_logger

#Get environment variables
MY_NAME = socket.gethostname()
BROKER = os.environ.get('BROKER_HOSTNAME')
BROKER_PORT = int(os.environ.get('BROKER_PORT'))
BROKER_CLOUD = os.environ.get('CLOUD_BROKER_HOSTNAME')
BROKER_CLOUD_PORT = int(os.environ.get('CLOUD_BROKER_PORT'))
NUM_OF_AGENTS= int(os.environ.get('AGENTS_NUMBER'))

# Set logging
logger = get_default_logger(MY_NAME)

# State, should be moved somewhere else
my_mates = []
my_mates_timers = {}
leader = None
current_election = {}
election = False
current_map = []

# Parameters
POLL_INTERVAL = 1 # seconds
AGENT_TTL = 3 # seconds
CLOUD_MODE = False

logger.info(f"My name is {MY_NAME}, Broker: {BROKER}")

def start_discovery():
    logger.debug(f"Starting local discovery")
    client_local.publish("agents/discovery/start", f"Initiate discovery!", qos=2)

def send_hello():
    client_local.publish(f"agents/discovery/hello", f"{MY_NAME}", qos=2)
    client_local.publish(f"map-service/hello", f"{MY_NAME}", qos=2)
    if CLOUD_MODE: client_cloud.publish(f"cloud-agent/hello", f"{MY_NAME}", qos=2)

def handle_discovery(candidate):
    if candidate != MY_NAME and candidate not in my_mates:
        my_mates.append(candidate)
        logger.info(f"New mate: {candidate}, My_mates: {my_mates}")
        my_mates_timers[candidate] = AGENT_TTL

    elif candidate != MY_NAME and candidate in my_mates:
        my_mates_timers[candidate] = AGENT_TTL
        logger.debug(f"Timer for {candidate} reset")

    if len(my_mates) == NUM_OF_AGENTS - 1 and not election and not leader:
        # find better way to initiate election
        logger.info(f"Discovery completed")
        start_election()

def check_liveness(seconds):
    for mate in my_mates:
        my_mates_timers[mate] -= seconds
        if my_mates_timers[mate] == 0:
            logger.warning(f"Agent {mate} is dead")
            my_mates.remove(mate)
            del my_mates_timers[mate]
            logger.info(f"Current mates: {my_mates}")

def start_election():
    global election, leader
    if election: return
    logger.info(f"Starting election")
    leader = None
    client_local.publish("agents/election/start", f"Starting election", qos=2)
    election = True

def send_vote():
    global election, leader
    election = True
    logger.info(f"There is new election, preparing my vote")
    # get random number
    random.seed()
    vote = random.randint(0, 100)
    # send vote
    client_local.publish("agents/election/vote", f"{MY_NAME}, {vote}", qos=2)

def receive_vote(agent, vote):
    logger.info(f"Receiving vote")
    current_election[agent] = vote
    if len(current_election) == len(my_mates):
        # find winner
        winner = max(current_election, key=current_election.get)
        election_completed(winner)

def election_completed(winner):
    global election, leader
    if not election: return
    logger.info(f"Election completed, winner is {winner}")
    leader = winner
    if winner == MY_NAME:
        logger.info(f"I am the leader({MY_NAME})")
        client_local.publish("agents/election/winner", f"{MY_NAME}", qos=2)
        logger.info(f"I will generate new map")
        client_local.publish("map-service/new-map", f"10", qos=2)
    else:
        logger.info(f"I am not the leader({MY_NAME})")
    current_election.clear()
    election = False

def adopt_new_map(new_map):
    global current_map
    current_map = new_map
    logger.info(f"New map adopted")

def send_info_backend():
    global current_map, leader, my_mates
    logger.info(f"Sending info to backend")
    data = {
        "leader": MY_NAME,
        "agents": my_mates+ [MY_NAME],
        "map": current_map
    }
    client_cloud.publish("backend/agents-info", json.dumps(data), qos=2)

def calculate_single(algo="a_star"):
    global current_map
    temp_map = copy.deepcopy(current_map)
    start = None
    end = None
    # Sanitize map from other agents
    for i, row in enumerate(temp_map):
        for j, cell in enumerate(row):
            if cell == f"{MY_NAME}-start": 
                    start = (i,j)
                    temp_map[i][j] = 0
            elif cell == f"{MY_NAME}-end":
                    end = (i,j)
                    temp_map[i][j] = 0
            elif cell == 0 or cell == 1:
                    pass
            else:
                    temp_map[i][j] = 0
    
    if not start or not end:
        logger.info(f"Start or end not found") 
        return

    logger.info(f"Agent: {MY_NAME} start: {start}, end: {end}")
    # create grid map
    grid_map = Grid_map(mode="no_diag")
    grid_map.load_from_list(temp_map)
    # get path
    possible, path = grid_map.find_path(start, end, algo=algo)
    if possible:
        logger.info(f"Path found: {path}")
        path_on_map = grid_map.path_on_map(path)
        client_cloud.publish("backend/path", json.dumps({"agent": MY_NAME, "path": path_on_map}), qos=2)
    else:
        logger.info(f"Path not found")


def on_subscribe(client_local, userdata, mid, granted_qos):
    logger.info("Subscribed to topic")

def on_message(client_local, userdata, msg):
    global election, leader
    msg_str = msg.payload.decode()
    match msg.topic:
        case "agents/discovery/start":
            send_hello()

        case "agents/discovery/hello":
            handle_discovery(msg_str)

        # Election
        case "agents/election/start":
            send_vote()

        case "agents/election/vote":
            agent, vote = msg_str.split(", ")
            receive_vote(agent, int(vote))

        case "agents/election/winner":
            election_completed(msg_str)

        case "agents/map/new":
            # map from json
            new_map = json.loads(msg_str)
            adopt_new_map(new_map)

        case "agents/info/all":
            if leader == MY_NAME: send_info_backend()

        case "agents/calculate/single_mode":
            logger.info(f"Calculating single path...")
            calculate_single(algo=msg_str)
        case _:
            logger.warning("Unknown topic")
            logger.warning(f"From topic: {msg.topic} | msg: {msg_str}")

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
client_local.subscribe(f"{MY_NAME}/#", qos=2)
client_local.subscribe(f"agents/#", qos=2)
client_cloud.subscribe(f"{MY_NAME}/#", qos=2)
client_cloud.subscribe(f"agents/#", qos=2)



client_local.loop_start()
client_cloud.loop_start()


while 1:
    start_discovery()
    check_liveness(POLL_INTERVAL)
    time.sleep(POLL_INTERVAL)



