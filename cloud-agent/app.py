from flask import Flask, render_template
from flask_mqtt import Mqtt
import socket
import os
import sys

BROKER_CLOUD = os.environ.get('CLOUD_BROKER_HOSTNAME')
BROKER_CLOUD_PORT = int(os.environ.get('CLOUD_BROKER_PORT'))
MY_NAME = socket.gethostname()
print(f"My name is {MY_NAME}, Broker: {BROKER_CLOUD}")

app = Flask(__name__)
app.config['MQTT_BROKER_URL'] = BROKER_CLOUD
app.config['MQTT_BROKER_PORT'] = BROKER_CLOUD_PORT
app.config['MQTT_USERNAME'] = "agent"
app.config['MQTT_PASSWORD'] = "agent-pass"
app.config['MQTT_KEEPALIVE'] = 5  # set the time interval for sending a ping to the broker to 5 seconds
app.config['MQTT_TLS_ENABLED'] = False  # set TLS to disabled for testing purposes

mqtt = Mqtt(app)
mqtt.publish(f"agent-0/hello", f"Hello from cloud!", qos=2)

@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe('cloud-agent/hello')
    mqtt.publish(f"agent-0/hello", f"Hello from cloud!", qos=2)

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    data = dict(
        topic=message.topic,
        payload=message.payload.decode()
    )
    print(data, file=sys.stderr)

@mqtt.on_log()
def handle_logging(client, userdata, level, buf):
    print(level, buf)

@app.route("/cloud-agent")
def serve():
    return "Hi there, I am a cloud-agent"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8888, debug=True)