from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

state = {
    "status": "idle",
    "text": ""
}


@app.get("/state")
def get_state():
    return jsonify(state)


@app.post("/state/<new_state>")
def set_state(new_state):
    state["status"] = new_state

    data = request.get_json(silent=True)

    if data and "text" in data:
        state["text"] = data["text"]

    return jsonify(state)


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )