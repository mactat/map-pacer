import copy, os, socket
import random, time, json
from libs.algo_lib import Grid_map
from libs.log_lib import get_default_logger
from libs.algo_lib_3d import Grid_map as Grid_map_3d
import paho.mqtt.client as mqtt
from prometheus_client import start_http_server, Summary, Enum
import ssl

#Get environment variables
MY_NAME = socket.gethostname()
BROKER = os.environ.get('BROKER_HOSTNAME')
BROKER_PORT = int(os.environ.get('BROKER_PORT'))
BROKER_CLOUD = os.environ.get('CLOUD_BROKER_HOSTNAME')
BROKER_CLOUD_PORT = int(os.environ.get('CLOUD_BROKER_PORT'))
SYSTEM_ID = os.environ.get('SYSTEM_ID')
TLS = os.environ.get('TLS') == "true"

# Set logging
logger = get_default_logger(MY_NAME)

# State, should be moved somewhere else
my_mates = []
my_mates_timers = {}
leader = None
start,end = None, None
current_election = {}
CUR_HIGHEST_ELECTION = 0
current_map = []
raw_map = []
election_started = False

# Parameters
POLL_INTERVAL = 1 # seconds
AGENT_TTL = 40 # seconds
CLOUD_MODE = False
DEFAULT_MAP_SIZE = 20

# Monitoring
monitoring_state = Enum(f"agent_state", 'State of the agents', states=['running', 'stopped'])
monitoring_leader = Enum('leader', 'Leader of the swarm', states=["yes","no"]) 
monitoring_setup_map_time = Summary('setup_map_time', 'Time spent for map setup')
monitoring_calculate_path_time = Summary('calculate_path_time', 'Time spent for path calculation')

start_http_server(8080)

logger.info(f"My name is {MY_NAME}, System Id: {SYSTEM_ID},Broker: {BROKER}")

def start_discovery():
    global leader, current_map
    logger.debug(f"Starting local discovery")
    client_local.publish(f"{SYSTEM_ID}/agents/discovery/start", f"Initiate discovery!", qos=0)
    if leader == MY_NAME:
        logger.debug(f"I am the leader, sending info to backend and agents")
        client_local.publish(f"{SYSTEM_ID}/agents/discovery/leader", json.dumps({"leader": MY_NAME, "map": current_map}), qos=0)
        send_info_backend()

def send_hello():
    client_local.publish(f"{SYSTEM_ID}/agents/discovery/hello", f"{MY_NAME}", qos=0)
    client_local.publish(f"{SYSTEM_ID}/map-service/hello", f"{MY_NAME}", qos=0)

def handle_discovery(candidate):
    global election_started, leader
    if candidate != MY_NAME and candidate not in my_mates:
        my_mates.append(candidate)
        logger.info(f"New mate: {candidate}, My_mates: {my_mates}")
        my_mates_timers[candidate] = AGENT_TTL
        # BUG!!! generate new map, should join the robot to current map instead...
        if MY_NAME == leader: 
            client_local.publish(f"{SYSTEM_ID}/map-service/random-map", f"{DEFAULT_MAP_SIZE}", qos=0)

    elif candidate != MY_NAME and candidate in my_mates:
        my_mates_timers[candidate] = AGENT_TTL
        logger.debug(f"Timer for {candidate} reset")

    if len(my_mates) > 0 and not leader and not election_started:
        # find better way to initiate election
        start_election()

def receive_leader(new_leader, new_map):
    global leader, election, current_election,CUR_HIGHEST_ELECTION, election_started, current_map
    election_started = False
    if new_leader == leader: return
    elif not leader:
        leader = new_leader
        current_election.clear()
        CUR_HIGHEST_ELECTION = 0
        #current_map = new_map
        # BUG!!!
        # how to get new_position ?
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
    client_local.publish(f"{SYSTEM_ID}/agents/election/start", f"{election_number}", qos=0)

def send_vote(election_number):
    global leader
    # get random number
    random.seed()
    vote = random.randint(0, 100)
    # send vote
    logger.debug(f"Sending vote: {vote} in election #{election_number}")
    client_local.publish(f"{SYSTEM_ID}/agents/election/vote", f"{election_number}, {MY_NAME}, {vote}", qos=0)

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

def cloud_calculate():
    logger.info("I will initiate cloud calculation")
    client_cloud.publish(f"cloud-agent/calculate/sequence_mode", json.dumps({
        "system_id": SYSTEM_ID,
        "map": raw_map,
        "agents": [MY_NAME] + my_mates
    }), qos=0)

def check_map():
    if leader != MY_NAME or current_map: return
    logger.info(f"No map available. I will generate new map")
    client_local.publish(f"{SYSTEM_ID}/map-service/random-map", f"{DEFAULT_MAP_SIZE}", qos=0)

def adopt_new_map(new_map):
    global current_map, raw_map, start, end
    raw_map = copy.deepcopy(new_map)
    current_map, start, end = sanitize_map(new_map)
    logger.info(f"New map adopted start:{start} end:{end}")

def sanitize_map(new_map):
    start, end = None, None
    # Sanitize map from other agents
    for i, row in enumerate(new_map):
        for j, cell in enumerate(row):
            if cell == f"{MY_NAME}-start": 
                    start = (i,j)
                    new_map[i][j] = 0
            elif cell == f"{MY_NAME}-end":
                    end = (i,j)
                    new_map[i][j] = 0
            elif cell == 0 or cell == 1:
                    pass
            else:
                    new_map[i][j] = 0
    return new_map, start, end

def send_info_backend():
    global current_map, leader, my_mates
    logger.debug(f"Sending info to backend")
    data = {
        "leader": MY_NAME,
        "agents": my_mates+ [MY_NAME],
        "map": current_map,
        "system_id": SYSTEM_ID
    }
    client_cloud.publish("backend/agents-info", json.dumps(data), qos=0)

@monitoring_calculate_path_time.time()
def calculate_single(algo="A*"):
    global current_map, start, end
    temp_map = copy.deepcopy(current_map)
    if not start or not end:
        logger.warning(f"Start or end not found")
        return

    logger.info(f"Agent: {MY_NAME} start: {start}, end: {end}")
    # create grid map
    grid_map = Grid_map(agent_num=MY_NUMBER, mode="no_diag")
    grid_map.load_from_list(temp_map)
    # get path
    possible, path = grid_map.find_path(start, end, algo=algo)
    if possible:
        # to be changed to dynamic
        full_path = path + [path[-1]*(100-len(path))]
        logger.info(f"Path found: {path}")
        client_cloud.publish("backend/path", json.dumps({"agent": MY_NAME, "path": full_path, "system_id": SYSTEM_ID}), qos=0)
    else:
        logger.info(f"Path not found")
        client_cloud.publish("backend/path", json.dumps({"agent": MY_NAME, "path": "not found", "system_id": SYSTEM_ID}), qos=0)

@monitoring_calculate_path_time.time()
def calculate_a_star(grid_map, start, end):
    possible, path = grid_map.a_star(start, end)
    return possible, path

@monitoring_setup_map_time.time()
def setup_map(current_map, paths):
    temp_map = copy.deepcopy(current_map)
    grid_map = Grid_map_3d(mode="no_diag")
    grid_map.load_from_list(temp_map)
    for path in paths:
        grid_map.mark_path_on_grid(path)
    return grid_map

def calculate_sequence(paths, sequence, status, algo="CA_star"):
    global current_map, leader
    if status == "start":
        if leader != MY_NAME: return
        logger.info("I will initiate the sequence calculation")
        sequence = [MY_NAME] + my_mates
        paths = []
    elif status != "continue" or sequence[0] != MY_NAME:
        return
    logger.info("It's my turn to calculate")

    if not start or not end:
        logger.warning(f"Start or end not found")
        client_cloud.publish("backend/path", json.dumps({"agent": MY_NAME, "path": "not found", "system_id": SYSTEM_ID}), qos=0)
        possible = False
    else:
        grid_map = setup_map(current_map, paths)
        possible, path = calculate_a_star(grid_map, start, end)
    if possible:
        logger.info(f"Path found: {path}")
        paths.append(path)
        client_cloud.publish("backend/path", json.dumps({"agent": MY_NAME, "path": [(x, y) for x,y,_ in path], "system_id": SYSTEM_ID}), qos=0)
    else:
        logger.info(f"Path not found")
        client_cloud.publish("backend/path", json.dumps({"agent": MY_NAME, "path": "not found", "system_id": SYSTEM_ID}), qos=0)
    # Last to calculate
    status = "continue"
    if len(sequence) == 1:
        status = "done"
        logger.info("Sequence calculation finished.")
    client_local.publish(f"{SYSTEM_ID}/agents/calculate/sequence_mode", json.dumps({"paths": paths, "sequence": sequence[1:], "status": status}), qos=0)

# ================= mqtt related functions ====================
def on_subscribe(client_local, userdata, mid, granted_qos):
    logger.info("Subscribed to topic")

def on_message(client_local, userdata, msg):
    global leader
    msg_str = msg.payload.decode()
    if msg.topic == f"{SYSTEM_ID}/agents/discovery/start":
        send_hello()

    elif msg.topic == f"{SYSTEM_ID}/agents/discovery/hello":
        handle_discovery(msg_str)

    elif msg.topic == f"{SYSTEM_ID}/agents/discovery/leader":
        data = json.loads(msg_str)
        receive_leader(data["leader"], data["map"])
    # Election
    elif msg.topic == f"{SYSTEM_ID}/agents/election/start":
        send_vote(msg_str)

    elif msg.topic == f"{SYSTEM_ID}/agents/election/vote":
        election_number, agent, vote = msg_str.split(", ")
        receive_vote(int(election_number), agent, int(vote))

    elif msg.topic == f"{SYSTEM_ID}/agents/map/new":
        # map from json
        new_map = json.loads(msg_str)
        adopt_new_map(new_map)

    elif msg.topic == f"{SYSTEM_ID}/agents/info/all":
        if leader == MY_NAME: send_info_backend()

    elif msg.topic == f"{SYSTEM_ID}/agents/calculate/single_mode":
        logger.info(f"Calculating single path...")
        calculate_single(algo=msg_str)
    elif msg.topic == f"{SYSTEM_ID}/agents/calculate/sequence_mode":
        data = json.loads(msg_str)
        calculate_sequence(data["paths"], data["sequence"], data["status"], algo="CA_star")
    elif msg.topic== f"{SYSTEM_ID}/agents/calculate/ca_star_cloud":
        logger.info("Received request to calculate with cloud")
        if leader == MY_NAME: cloud_calculate()
    else:
        logger.warning("Unknown topic")
        logger.warning(f"From topic: {msg.topic} | msg: {msg_str}")

def monitor():
    global leader
    monitoring_state.state('running')
    if MY_NAME==leader:
        monitoring_leader.state('yes')
    else:
        monitoring_leader.state('no')

client_local = mqtt.Client(client_id=MY_NAME, clean_session=False)
client_local.username_pw_set(username="agent", password="agent-pass")
client_local.on_subscribe = on_subscribe
client_local.on_message = on_message
client_local.connect(BROKER, BROKER_PORT)

client_cloud = mqtt.Client(client_id=MY_NAME, transport='websockets', clean_session=False)
client_cloud.ws_set_options(path="/mqtt", headers=None)

##### COMMENT TO RUN WITH TILT TODO: fix it
if TLS:
    client_cloud.tls_set(tls_version=2, cert_reqs=ssl.CERT_NONE)
    client_cloud.tls_insecure_set(True)
#####

client_cloud.username_pw_set(username="agent", password="agent-pass")
client_cloud.on_subscribe = on_subscribe
client_cloud.on_message = on_message
client_cloud.connect(BROKER_CLOUD, BROKER_CLOUD_PORT)

# Subscribe for related topics
client_local.subscribe(f"{SYSTEM_ID}/{MY_NAME}/#", qos=0)
client_local.subscribe(f"{SYSTEM_ID}/agents/#", qos=0)
client_cloud.subscribe(f"{SYSTEM_ID}/{MY_NAME}/#", qos=0)
client_cloud.subscribe(f"{SYSTEM_ID}/agents/#", qos=0)



client_local.loop_start()
client_cloud.loop_start()


while 1:
    start_discovery()
    check_liveness(POLL_INTERVAL)
    check_map()
    monitor()
    time.sleep(POLL_INTERVAL)



