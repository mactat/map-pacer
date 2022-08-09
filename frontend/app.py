from flask import Flask, render_template
app = Flask(__name__)

@app.route("/")
def serve():
    return "Hi there, I am a cloud agent"

if __name__ == "__main__":
    app.run(port=8888)