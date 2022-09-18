
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
MY_NUMBER = int(MY_NAME[-1])
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
CUR_HIGHEST_ELECTION = 0
current_map = []
election_started = False

# Parameters
POLL_INTERVAL = 1 # seconds
AGENT_TTL = 4 # seconds
CLOUD_MODE = False
DEFAULT_MAP_SIZE = 30

logger.info(f"My name is {MY_NAME}, Broker: {BROKER}")

def start_discovery():
    global leader
    logger.debug(f"Starting local discovery")
    client_local.publish("agents/discovery/start", f"Initiate discovery!", qos=2)
    if leader == MY_NAME:
        logger.debug(f"I am the leader, sending info to backend and agents")
        client_local.publish("agents/discovery/leader", f"{MY_NAME}", qos=2)
        send_info_backend()

def send_hello():
    client_local.publish(f"agents/discovery/hello", f"{MY_NAME}", qos=2)
    client_local.publish(f"map-service/hello", f"{MY_NAME}", qos=2)
    if CLOUD_MODE: client_cloud.publish(f"cloud-agent/hello", f"{MY_NAME}", qos=2)

def handle_discovery(candidate):
    global election_started
    if candidate != MY_NAME and candidate not in my_mates:
        my_mates.append(candidate)
        logger.info(f"New mate: {candidate}, My_mates: {my_mates}")
        my_mates_timers[candidate] = AGENT_TTL

    elif candidate != MY_NAME and candidate in my_mates:
        my_mates_timers[candidate] = AGENT_TTL
        logger.debug(f"Timer for {candidate} reset")

    if len(my_mates) > 0 and not leader and not election_started:
        # find better way to initiate election
        start_election()

def receive_leader(new_leader):
    global leader, election, current_election,CUR_HIGHEST_ELECTION, election_started
    election_started = False
    if new_leader == leader: return
    elif not leader:
        leader = new_leader
        current_election.clear()
        CUR_HIGHEST_ELECTION = 0
        logger.info(f"Got leader info, leader is {leader}")
    else:
        logger.warning(f"Leader mismatch, old: {leader}, new: {new_leader}. Initiating election")
        start_election()

def check_liveness(seconds):
    global leader
    for mate in my_mates:
        my_mates_timers[mate] -= seconds
        if my_mates_timers[mate] == 0:
            logger.warning(f"Agent {mate} is dead")
            my_mates.remove(mate)
            del my_mates_timers[mate]
            if mate == leader:
                logger.warning(f"Leader {mate} is dead")
                leader = None
                start_election()
            logger.info(f"Current mates: {my_mates}")

def start_election():
    global leader, election_started
    election_started = True
    current_election.clear()
    leader = None
    # Generate random election number
    random.seed()
    election_number = random.randint(0, 100)
    logger.info(f"Starting election #{election_number}")
    client_local.publish("agents/election/start", f"{election_number}", qos=2)

def send_vote(election_number):
    global leader
    # get random number
    random.seed()
    vote = random.randint(0, 100)
    # send vote
    logger.debug(f"Sending vote: {vote} in election #{election_number}")
    client_local.publish("agents/election/vote", f"{election_number}, {MY_NAME}, {vote}", qos=2)

def receive_vote(election_number, agent, vote):
    global current_election, CUR_HIGHEST_ELECTION, leader
    if election_number < CUR_HIGHEST_ELECTION: return
    elif election_number == CUR_HIGHEST_ELECTION:
        current_election[agent] = vote
    elif election_number > CUR_HIGHEST_ELECTION:
        CUR_HIGHEST_ELECTION = election_number
        logger.info(f"More important election #{election_number} started")
        current_election.clear()
        current_election[agent] = vote
    logger.debug(f"Receiving vote in election #{election_number}: {agent} - {vote}")
    # current_election[agent] = vote
    if len(current_election) != len(my_mates): return
    # find winner
    winner = max(current_election, key=current_election.get)
    if winner != MY_NAME: return
    leader = MY_NAME
    logger.info(f"I am the leader({MY_NAME})")


def check_map():
    if leader != MY_NAME or current_map: return
    logger.info(f"No map available. I will generate new map")
    client_local.publish("map-service/random-map", f"{DEFAULT_MAP_SIZE}", qos=2)

def adopt_new_map(new_map):
    global current_map
    current_map = new_map
    logger.info(f"New map adopted")

def send_info_backend():
    global current_map, leader, my_mates
    logger.debug(f"Sending info to backend")
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
    grid_map = Grid_map(agent_num=MY_NUMBER, mode="no_diag")
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
    global leader
    msg_str = msg.payload.decode()
    match msg.topic:
        case "agents/discovery/start":
            send_hello()

        case "agents/discovery/hello":
            handle_discovery(msg_str)

        case "agents/discovery/leader":
            receive_leader(msg_str)
        # Election
        case "agents/election/start":
            send_vote(msg_str)

        case "agents/election/vote":
            election_number, agent, vote = msg_str.split(", ")
            receive_vote(int(election_number), agent, int(vote))

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
    check_map()
    time.sleep(POLL_INTERVAL)



