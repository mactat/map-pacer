from visualizer import visualize_paths
from libs.log_lib import get_default_logger
from flask import Flask, render_template, request
from flask_mqtt import Mqtt
import socket
import os
import sys
import json
from flask_cors import CORS


BROKER_CLOUD = os.environ.get('CLOUD_BROKER_HOSTNAME')
BROKER_CLOUD_PORT = int(os.environ.get('CLOUD_BROKER_PORT'))
MY_NAME = socket.gethostname()

# This will be in DB
paths = {}

print(f"My name is {MY_NAME}, Broker: {BROKER_CLOUD}")
logger = get_default_logger(MY_NAME)

app = Flask(__name__)
CORS(app)
app.config['MQTT_BROKER_URL'] = BROKER_CLOUD
app.config['MQTT_BROKER_PORT'] = BROKER_CLOUD_PORT
app.config['MQTT_USERNAME'] = "agent"
app.config['MQTT_PASSWORD'] = "agent-pass"
app.config['MQTT_KEEPALIVE'] = 5  # set the time interval for sending a ping to the broker to 5 seconds
app.config['MQTT_TLS_ENABLED'] = False  # set TLS to disabled for testing purposes
info = {"agents":"", "leader":"", "map": []}
mqtt = Mqtt(app)


def save_path(agent, path):
    paths[agent] = path


@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe('backend/#')

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    global info, paths
    topic=message.topic,
    payload=message.payload.decode()
    match topic[0]:
        case "backend/agents-info":
            temp_info = json.loads(payload)
            if not info["map"] or temp_info["map"] != info["map"]:
                logger.info("Detected map change")
                paths = {}
            logger.info("Info received")
            info = temp_info
        case "backend/path":
            logger.info("Path received")
            data = json.loads(payload)
            save_path(data["agent"], data["path"])
        case _:
            print("Unknown topic", file=sys.stderr)
            print(f"From topic: {topic} | msg: {payload}", file=sys.stderr)

@mqtt.on_log()
def handle_logging(client, userdata, level, buf):
    print(level, buf)

@app.route("/backend/test")
def serve():
    return "Hi there, I am a backend service!"

@app.route("/backend/discovery")
def trigger_discovery():
    mqtt.publish("agents/discovery/start", "Backend service is here!", qos=2)
    return "Discovery triggered!"

@app.route("/backend/new-map")
def generate_map():
    args = request.args
    paths.clear()
    size = args.get("size", default="10")
    mqtt.publish("map-service/random-map", size, qos=2)
    return "New map requested!"

@app.route("/backend/map-from-file")
def get_map_from_file():
    args = request.args
    paths.clear()
    map_file = args.get("map_file", default="random")
    mqtt.publish("map-service/map-from-file", f"{map_file}.txt", qos=2)
    return "New map requested!"

@app.route("/backend/refresh-info")
def refresh_info():
    mqtt.publish("agents/info/all", "empty", qos=2)
    return "Info requested!"

@app.route("/backend/get-info")
def get_info():
    global info
    return info

@app.route("/backend/single_calculate")
def single_calculate():
    global info
    args = request.args
    algo = args.get("algo", default="A*")
    mqtt.publish("agents/calculate/single_mode", algo, qos=2)
    return f"Calculation requested with algorithm: {algo}!"

@app.route("/backend/show_paths")
def show_paths():
    global paths
    paths_str = "\n\n".join([f"<h1>{agent}:</h1>\n {path}" for agent, path in paths.items()]).replace('\n', '<br>')
    return paths_str

@app.route("/backend/get_paths")
def get_paths():
    global paths
    return json.dumps(paths)

@app.route("/backend/clear_paths")
def clear_paths():
    global paths
    paths = {}
    return "ok"

@app.route("/backend/sequence_calculate")
def sequence_calculate():
    global info
    data = json.dumps({"paths": [], "sequence": [], "status": "start"})
    mqtt.publish("agents/calculate/sequence_mode", data, qos=2)
    return f"Calculation requested!"

@app.route("/backend/sequence_calculate_cloud")
def sequence_calculate_cloud():
    data = json.dumps({"algo":"CA*"})
    mqtt.publish("cloud-agent/calculate/sequence_mode", data, qos=2)
    return f"Calculation requested!"

# TODO: frontend shoud use this function rather than refreshing the page
@app.route("/backend/get_prerendered_map")
def get_prerendered_map():
    global info, paths
    if not info:
        return ["No info or paths"]
    return json.dumps(visualize_paths(info["map"], list(paths.values())))

@app.route("/backend/save_map", methods=['GET', 'POST'])
def save_map():
    new_map = json.dumps(request.json)
    mqtt.publish("map-service/save-map", new_map, qos=2)
    return "ok"

@app.route("/backend/adopt_map", methods=['GET', 'POST'])
def adopt_new_map():
    new_map = json.dumps(request.json)
    mqtt.publish("map-service/adopt-map", new_map, qos=2)
    return "ok"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8888, debug=True)