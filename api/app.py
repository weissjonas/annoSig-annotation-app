from datetime import datetime
import json
from flask import Flask, request


app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World!\n'


@app.route('/upload', methods=['POST'])
def upload_file():
    data = request.get_json()
    filename = f"data-{datetime.now().timestamp()}.json"

    # TODO: Validation before writing to file
    with open(filename, 'wb') as f:
        json.dump(data, f, indent=2)

    return ''
