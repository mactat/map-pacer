from flask import Flask, render_template
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

@app.route("/")
def serve():
    return render_template("visualize.html")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8888, debug=True)