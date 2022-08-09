from flask import Flask, render_template
app = Flask(__name__)

@app.route("/")
def serve():
    return "Hi there, I am a frontend"

if __name__ == "__main__":
    app.run(port=8888)