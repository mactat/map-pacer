from flask import Flask, render_template, request, send_from_directory
from flask_cors import CORS
import os
from waitress import serve

app = Flask(__name__)
CORS(app)
BACKEND_URL = os.environ.get('BACKEND_URL')


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                          'favicon.ico',mimetype='image/vnd.microsoft.icon')


@app.route("/")
def main():
    return render_template("main.html", backend_url=BACKEND_URL)

@app.route("/map-creator")
def map_creator():
    args = request.args
    agents_color = ["red", "blue", "green", "yellow"]
    num_of_agents = int(args.get("num_of_agents", default=1))
    return render_template("map_creator.html", num_of_agents=num_of_agents, agents_color=agents_color[:num_of_agents], backend_url=BACKEND_URL)
# TODO:
# - dynamic map-names fetching from backend
# - start and stop for each agent stored in backend
# - agent state (idle, computing, dead) in backend
# - map creator
# - forcing agent start end in map service
# - map service stores agent start and end positions
# - map service can spawn agent on EXISTING map
# - droping agents start end on the map


if __name__ == "__main__":
    serve(app, port='8888')
    #app.run(host='0.0.0.0', port=8888, debug=True)