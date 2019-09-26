from datetime import datetime
import json
from flask import Flask, request, abort


API_TOKEN = "0e2d70b1f642f85550adb7ff20656462"

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World!\n'


@app.route('/upload', methods=['POST'])
def upload_file():
    token = request.headers.get("Authorization")
    if token != API_TOKEN:
        abort(401)

    data = request.get_json()
    filename = f"data-{datetime.now().timestamp()}.json"

    # TODO: Validation before writing to file
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

    return ''
