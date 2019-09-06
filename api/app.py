from flask import Flask, request
app = Flask(__name__)

app.data_index = 0

@app.route('/')
def hello_world():
    return 'Hello, World!\n'

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():

    print('data', request.get_json())
    with open(f'data{app.data_index}.json', 'wb') as f:
        f.write(request.get_data())
        app.data_index += 1

        # if request.files:
        #     f = request.files['the_file']
        #     f.save('uploaded_file.txt')

    return 'upload complete\n'
