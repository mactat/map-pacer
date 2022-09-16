from flask import Flask, render_template, request
from flask_mqtt import Mqtt
import socket
import os
import sys
import json

BROKER_CLOUD = os.environ.get('CLOUD_BROKER_HOSTNAME')
BROKER_CLOUD_PORT = int(os.environ.get('CLOUD_BROKER_PORT'))
MY_NAME = socket.gethostname()

# This will be in DB
paths = {}

print(f"My name is {MY_NAME}, Broker: {BROKER_CLOUD}")

app = Flask(__name__)
app.config['MQTT_BROKER_URL'] = BROKER_CLOUD
app.config['MQTT_BROKER_PORT'] = BROKER_CLOUD_PORT
app.config['MQTT_USERNAME'] = "agent"
app.config['MQTT_PASSWORD'] = "agent-pass"
app.config['MQTT_KEEPALIVE'] = 5  # set the time interval for sending a ping to the broker to 5 seconds
app.config['MQTT_TLS_ENABLED'] = False  # set TLS to disabled for testing purposes
info = {}
mqtt = Mqtt(app)


def save_path(agent, path):
    paths[agent] = path


@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe('backend/#')

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    global info
    topic=message.topic,
    payload=message.payload.decode()
    match topic[0]:
        case "backend/agents-info":
            info = json.loads(payload)
        case "backend/path":
            print("Path received")
            info = json.loads(payload)
            save_path(info["agent"], info["path"])
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
    refresh_info()
    return info

@app.route("/backend/single-agent-calculate")
def single_calculate():
    global info
    args = request.args
    algo = args.get("algo", default="a_star")
    mqtt.publish("agents/calculate/single_mode", algo, qos=2)
    return f"Calculation requested with algorithm: {algo}!"

@app.route("/backend/show_paths")
def show_paths():
    global paths
    paths_str = "\n\n".join([f"<h1>{agent}:</h1>\n {path}" for agent, path in paths.items()]).replace('\n', '<br>')
    return paths_str


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8888, debug=True)