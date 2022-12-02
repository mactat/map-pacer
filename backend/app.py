from visualizer import visualize_paths
from libs.log_lib import get_default_logger
from libs.db_lib import Database
from flask import Flask, render_template, request
from flask_mqtt import Mqtt
import socket
import os
import json
from flask_cors import CORS
from waitress import serve


BROKER_CLOUD = os.environ.get('CLOUD_BROKER_HOSTNAME')
BROKER_CLOUD_PORT = int(os.environ.get('CLOUD_BROKER_PORT'))
MY_NAME = socket.gethostname()

print(f"My name is {MY_NAME}, Broker: {BROKER_CLOUD}")
# Set logging
logger = get_default_logger(MY_NAME)

app = Flask(__name__)
CORS(app)
app.config['MQTT_BROKER_URL'] = BROKER_CLOUD
app.config['MQTT_BROKER_PORT'] = BROKER_CLOUD_PORT
app.config['MQTT_USERNAME'] = "agent"
app.config['MQTT_PASSWORD'] = "agent-pass"
app.config['MQTT_CLIENT_ID'] = MY_NAME
app.config['MQTT_KEEPALIVE'] = 30
# set TLS to disabled for testing purposes
app.config['MQTT_TLS_ENABLED'] = False
info = {"agents": "", "leader": "", "map": []}
mqtt = Mqtt(app)

# Handle DB
DB_USERNAME = os.environ.get('DB_USERNAME')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_HOSTNAME = os.environ.get('DB_HOSTNAME')
DB_PORT = int(os.environ.get('DB_PORT'))

database = Database(DB_USERNAME, DB_PASSWORD, DB_HOSTNAME, DB_PORT)
database.create_table("systems")


def save_path(system_id, agent, path, time):
    agents, leader, cur_map, paths, times = database.get_data(system_id)
    if not paths:
        paths = {}
        times = {}
    paths[agent] = path
    times[agent] = time
    full_data = {"agents": agents, "leader": leader,
                 "map": cur_map, "paths": paths, "times": times}
    database.update_data(system_id=system_id, data=full_data)


@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info('Connected successfully')
    else:
        logger.error(f"{client}, {userdata}, {flags}, {rc}")


@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    topic = message.topic,
    payload = message.payload.decode()
    match topic[0]:
        case "backend/agents-info":
            temp_info = json.loads(payload)
            logger.info(f"Received system info from {temp_info['system_id']}")
            agents, leader, cur_map, paths, times = database.get_data(
                temp_info['system_id'])
            if not cur_map or temp_info["map"] != cur_map:
                logger.info("Detected map change")
                paths = {}
                times = {}
            full_data = {"agents": temp_info['agents'], "leader": temp_info['leader'],
                         "map": temp_info["map"], "paths": paths, "times": times}
            database.update_data(
                system_id=temp_info['system_id'], data=full_data)
        case "backend/path":
            data = json.loads(payload)
            logger.info(f"Path received: {data['system_id']}, {data['agent']}, {data['time']}")
            save_path(data['system_id'], data["agent"],
                      data["path"], data["time"])
        case _:
            logger.error(f"Unknown topic: {topic} | msg: {payload}")


@mqtt.on_log()
def handle_logging(client, userdata, level, buf):
    print(level, buf)


@app.route("/backend/test")
def test():
    return "Hi there, I am a backend service!"


@app.route("/backend/discovery")
def trigger_discovery():
    args = request.args
    system_id = args.get("system_id", default="test")
    mqtt.publish(f"{system_id}/agents/discovery/start",
                 "Backend service is here!", qos=0)
    return "Discovery triggered!"


@app.route("/backend/new-map")
def generate_map():
    args = request.args
    paths.clear()
    size = args.get("size", default="10")
    system_id = args.get("system_id", default="test")
    mqtt.publish(f"{system_id}/map-service/random-map", size, qos=0)
    return "New map requested!"


@app.route("/backend/map-from-file")
def get_map_from_file():
    args = request.args
    clear_paths()
    map_file = args.get("map_file", default="random")
    system_id = args.get("system_id", default="test")
    mqtt.publish(f"{system_id}/map-service/map-from-file",
                 f"{map_file}.txt", qos=0)
    logger.info(f"Published: {system_id}/map-service/map-from-file")
    return "New map requested!"


@app.route("/backend/refresh-info")
def refresh_info():
    args = request.args
    system_id = args.get("system_id", default="test")
    mqtt.publish(f"{system_id}/agents/info/all", "empty", qos=0)
    return "Info requested!"


@app.route("/backend/get-info")
def get_info():
    args = request.args
    system_id = args.get("system_id", default="test")
    agents, leader, cur_map, paths, times = database.get_data(system_id)
    info = {"agents": agents, "leader": leader, "map": cur_map, "paths": paths, "times": times}
    return json.dumps(info)


@app.route("/backend/single_calculate")
def single_calculate():
    args = request.args
    algo = args.get("algo", default="A*")
    system_id = args.get("system_id", default="test")
    mqtt.publish(f"{system_id}/agents/calculate/single_mode", algo, qos=0)
    return f"Calculation requested with algorithm: {algo}!"


@app.route("/backend/show_paths")
def show_paths():
    global paths
    paths_str = "\n\n".join(
        [f"<h1>{agent}:</h1>\n {path}" for agent, path in paths.items()]).replace('\n', '<br>')
    return paths_str


@app.route("/backend/get_paths")
def get_paths():
    args = request.args
    system_id = args.get("system_id", default="test")
    _, _, _, paths, _ = database.get_data(system_id)
    return json.dumps(paths)


@app.route("/backend/get_times")
def get_times():
    args = request.args
    system_id = args.get("system_id", default="test")
    _, _, _, _, times = database.get_data(system_id)
    return json.dumps(times)


@app.route("/backend/clear_paths")
def clear_paths():
    args = request.args
    system_id = args.get("system_id", default="test")
    agents, leader, cur_map, _, _ = database.get_data(system_id)
    full_data = {"agents": agents, "leader": leader,
                 "map": cur_map, "paths": {}, "times": {}}
    database.update_data(system_id=system_id, data=full_data)
    return "ok"


@app.route("/backend/sequence_calculate")
def sequence_calculate():
    args = request.args
    system_id = args.get("system_id", default="test")
    data = json.dumps({"paths": [], "sequence": [], "status": "start"})
    mqtt.publish(f"{system_id}/agents/calculate/sequence_mode", data, qos=0)
    return f"Calculation requested!"


@app.route("/backend/single_calculate_cloud")
def single_calculate_cloud():
    args = request.args
    system_id = args.get("system_id", default="test")
    algo = args.get("algo", default="A*")
    data = json.dumps({"algo": algo})
    mqtt.publish(
        f"{system_id}/agents/calculate/single_calculate_cloud", data, qos=0)
    return f"Calculation requested!"


@app.route("/backend/sequence_calculate_cloud")
def sequence_calculate_cloud():
    args = request.args
    system_id = args.get("system_id", default="test")
    data = json.dumps({"algo": "CA*"})
    mqtt.publish(f"{system_id}/agents/calculate/ca_star_cloud", data, qos=0)
    return f"Calculation requested!"


@app.route("/backend/get_prerendered_map")
def get_prerendered_map():
    args = request.args
    system_id = args.get("system_id", default="test")
    _, _, cur_map, paths, _ = database.get_data(system_id)
    if not cur_map:
        return [False]
    return json.dumps(visualize_paths(cur_map, list(paths.values())))


@app.route("/backend/save_map", methods=['GET', 'POST'])
def save_map():
    args = request.args
    system_id = args.get("system_id", default="test")
    new_map = json.dumps(request.json)
    mqtt.publish(f"{system_id}/map-service/save-map", new_map, qos=0)
    return "ok"


@app.route("/backend/adopt_map", methods=['GET', 'POST'])
def adopt_new_map():
    args = request.args
    system_id = args.get("system_id", default="test")
    new_map = json.dumps(request.json)
    mqtt.publish(f"{system_id}/map-service/adopt-map", new_map, qos=0)
    return "ok"


@app.route("/backend/get_systems")
def get_systems():
    systems_raw = json.dumps(database.get_systems())
    return systems_raw


database.get_systems()
if __name__ == "__main__":
    mqtt.subscribe('backend/#', 0)
    serve(app, port='8888')
    #app.run(host='0.0.0.0', port=8888, debug=True)
