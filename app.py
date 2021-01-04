from flask import Flask
from flask import request
from flask import jsonify

app = Flask(__name__)

accumulated = 0
counter = 0
average = None

def add_value(value):
    global counter, accumulated, average
    counter += 1
    accumulated += value
    average = accumulated / counter

@app.route('/')
def index():
    return 'Hello world'

@app.route('/sum', methods=['POST'])
def sum():
    value = request.args.get('value')
    if value is None:
        return 'You must send the value URL param'
    value = int(value)
    if value < 0:
        return 'Value param must be an integer equal or greater than 0', 400
    add_value(value)
    return 'value: {} acummulated: {}'.format(value, accumulated), 200

@app.route('/info', methods=['GET'])
def info():
    global accumulated, average, counter
    return jsonify({
        "total": accumulated,
        "count": counter,
        "average": average
    })

if __name__ == '__main__':
    app.run(debug = True)