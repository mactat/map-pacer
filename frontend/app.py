from flask import Flask, render_template, request
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

@app.route("/")
def serve():
    return render_template("main.html")

@app.route("/map-creator")
def map_creator():
    args = request.args
    agents_color = ["red", "blue", "green", "yellow"]
    num_of_agents = int(args.get("num_of_agents", default=1))
    return render_template("map_creator.html", num_of_agents=num_of_agents, agents_color=agents_color[:num_of_agents])
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
    app.run(host='0.0.0.0', port=8888, debug=True)