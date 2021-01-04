from flask import Flask
from flask import request
from flask import jsonify

app = Flask(__name__)

accumulated = 0
counter = 0
average = None

people_list = []


def add_value(value):
    global counter, accumulated, average
    counter += 1
    accumulated += value
    average = accumulated / counter


def people_exist(dni):
    if len(people_list) > 0:
        for ppl in people_list:
            if ppl['dni'] == dni:
                return True
    return False


@app.route('/')
def index():
    return jsonify({
        "messege": "Hi! The root route is empty. Try with /sum or /info endpoints",
        "status": 400
    }), 400

@app.route('/sum', methods=['POST'])
def sum():
    value = request.args.get('value')
    if value is None:
        return 'You must send the value URL param'
    value = int(value)
    if value < 0:
        return 'Value param must be an integer equal or greater than 0', 400
    add_value(value)
    return '', 200

@app.route('/info', methods=['GET'])
def info():
    global accumulated, average, counter
    return jsonify({
        "total": accumulated,
        "count": counter,
        "average": average
    })


@app.route('/people', methods=['POST', 'GET'])
def people():
    if request.method == 'POST':

        req_data = request.get_json()
        name = None
        dni = None
        height = None
        if 'name' in req_data and 'dni' in req_data and 'height' in req_data:
            name = req_data['name']
            dni = req_data['dni']
            height = req_data['height']
            if type(name) == str and type(dni) == int and type(height) == float:
                if people_exist(dni):
                    return 'a person with dni {} already exists in the system'.format(dni), 409
                else:
                    people_list.append(req_data)
                    return jsonify({
                        "messege": "success"
                    }), 201
        return {
            "messege": "400 - BAD REQUEST",
            "expected": {
                "name": "<str value>",
                "dni": "<int value>",
                "height": "<float value>" 
            }
        }, 400
    

    if request.method == 'GET':
        
        args = request.args.get('dni', None)
        
        if args is not None:
            dni = int(args)
            for ppl in people_list:
                if ppl['dni'] == dni:
                    return jsonify(ppl), 200
        
            return '', 204
        
        return jsonify(people_list), 200



if __name__ == '__main__':
    app.run(debug = True)