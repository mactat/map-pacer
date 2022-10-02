from flask import Flask, render_template
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

@app.route("/")
def serve():
    return render_template("visualize.html")
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