from flask import Flask
from flask import request
from flask import jsonify

app = Flask(__name__)

accumulated = counter = average = 0
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
                return ppl
            else:
                return False
    else:
        return False

def validate_types(name, dni, height):
    if type(name) == str and type(dni) == int and type(height) == float:
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
    value = request.args.get('value', None)
    if not value:
        return 'You must send the value URL param'
    else:
        if int(value) < 0:
            return 'Value param must be an integer equal or greater than 0', 400
        else:
            add_value(int(value))
            return '', 200

@app.route('/info', methods=['GET'])
def info():
    global accumulated, average, counter
    return jsonify({
        "total": accumulated,
        "count": counter,
        "average": average
    })


@app.route('/people', methods=['POST', 'GET', 'DELETE'])
def people():

    bad_req_response_expected = {
            "messege": "400 - BAD REQUEST",
            "expected": {
                "name": "<str value>",
                "dni": "<int value>",
                "height": "<float value>" 
            }
        }

    if request.method == 'POST':

        req_data = request.get_json(silent=True)
        if req_data is None:
            return jsonify(bad_req_response_expected), 400

        name = dni = height = None

        if 'name' in req_data and 'dni' in req_data and 'height' in req_data:
            name = req_data['name']
            dni = req_data['dni']
            height = req_data['height']

            if validate_types(name, dni, height) and not people_exist(dni):
                people_list.append(req_data)
                return jsonify({
                    "messege": "success"
                }), 201
            else:
                if(people_exist(dni)):
                    return 'a person with dni {} already exists in the system'.format(dni), 409
                else:
                    return jsonify(bad_req_response_expected), 400
        else:
            return jsonify(bad_req_response_expected), 400
    

    if request.method == 'GET':
        dni = request.args.get('dni', None)
        if dni:
            try:
                dni = int(dni)
            except:
                return jsonify({
                    "messege": "expected a <int> value for the key 'dni'"
                }), 400
            ppl = people_exist(dni)
            if ppl:
                return jsonify(ppl),200
            else:
                return '', 204
        else:
            return jsonify(people_list), 200

    if request.method == 'DELETE':
        dni = request.args.get('dni', None)
        if dni:
            try:
                dni = int(dni)
            except:
                return jsonify({
                    "messege": "expected a <int> value for the key 'dni'"
                }), 400
            founded = [ppl for ppl in people_list if ppl['dni'] == dni]
            if len(founded) > 0:
                people_list.remove(founded[0])
                return '', 200
            else:
                return jsonify({
                    "messege": "dni {} not found".format(dni)
                }), 204
        else:
            return '', 400


@app.route('/hora-arg')
def datetime():
    r = requests.get('http://worldtimeapi.org/api/timezone/ETC/UTC')
    if r.status_code == 200:
        req_json = r.json()
        unixtime = int(req_json['unixtime'])
        utc_arrow_obj = arrow.get(unixtime)
        time_formated_arg = utc_arrow_obj.to('GMT-3').format('DD/MM/YYYY HH:mm:ss')
        return '{}'.format(time_formated_arg), 200
    else:
        date_utc_now = arrow.utcnow()
        date_utc_now = date_utc_now.to('GMT-3').format('DD/MM/YYYY HH:mm:ss')
        return '{}'.format(date_utc_now), 200



if __name__ == '__main__':
    app.run(debug = True)