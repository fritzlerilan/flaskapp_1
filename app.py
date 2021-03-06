from flask import Flask
from flask import request
from flask import jsonify
from flask import Response
from datetime import datetime
from flask_pymongo import PyMongo
from bson import json_util
import arrow
import requests



NAME = "name"
DNI = "dni"
HEIGHT = "height"
PEOPLE_DB_URL = "mongodb://localhost:27017/peopledb_test"
NULL = "null"


app = Flask(__name__)
app.config["MONGO_URI"] = PEOPLE_DB_URL

mongo = PyMongo(app)

accumulated = counter = average = 0


def add_value(value):
    global counter, accumulated, average
    counter += 1
    accumulated += value
    average = accumulated / counter


def people_exist_in_db(dni):
    if json_util.dumps(mongo.db.people.find_one({DNI: dni})) == NULL:
        return False
    return True


def validate_types(name, dni, height):

    if type(name) == str and type(dni) == int and type(height) == float:
        return True
    return False

@app.route("/")
def index():
    return (
        jsonify(
            {
                "messege": "Hi! The root route is empty. Try with /sum or /info endpoints",
                "status": 400,
            }
        ),
        400,
    )


@app.route("/sum", methods=["POST"])
def sum():
    value = request.args.get("value", None)
    if not value:
        return "You must send the value URL param"
    else:
        if int(value) < 0:
            return "Value param must be an integer equal or greater than 0", 400
        else:
            add_value(int(value))
            return "", 200


@app.route("/info", methods=["GET"])
def info():
    global accumulated, average, counter
    return jsonify({"total": accumulated, "count": counter, "average": average})


@app.route("/people", methods=["POST", "GET", "DELETE"])
def people():

    bad_req_response_expected = {
        "messege": "400 - BAD REQUEST",
        "expected": {
            NAME: "<str value>",
            DNI: "<int value>",
            HEIGHT: "<float value>",
        },
    }

    if request.method == "POST":

        req_data = request.get_json(silent=True)
        if req_data is None:
            return jsonify(bad_req_response_expected), 400

        if {NAME,DNI,HEIGHT} <= req_data.keys():
            person = {
                NAME: req_data[NAME],
                DNI: req_data[DNI],
                HEIGHT: req_data[HEIGHT],
            }

            if validate_types(
                person[NAME], person[DNI], person[HEIGHT]) and people_exist_in_db(person[DNI]) == False:
                id = mongo.db.people.insert(person)
                return jsonify({"messege": "success with id {}".format(str(id))}), 201
            else:
                if people_exist_in_db(person[DNI]):
                    return (
                        "a person with dni {} already exists in the system".format(
                            person[DNI]
                        ),
                        409,
                    )
                else:
                    return jsonify(bad_req_response_expected), 400
        else:
            return jsonify(bad_req_response_expected), 400

    if request.method == "GET":
        dni = request.args.get(DNI, None)
        if dni:
            try:
                dni = int(dni)
            except:
                return (
                    jsonify({"messege": "expected a <int> value for the key 'dni'"}),
                    400,
                )
            person = json_util.dumps(mongo.db.people.find_one({DNI: dni}))
            if person != NULL:
                response = Response(person, mimetype="application/json")
                response.status_code = 200
                return response
            else:
                return "", 204
        else:
            people = mongo.db.people.find()
            response = json_util.dumps(people)
            return Response(response, mimetype="application/json")

    if request.method == "DELETE":
        dni = request.args.get(DNI, None)
        if dni:
            try:
                dni = int(dni)
            except:
                return (
                    jsonify({"messege": "expected a <int> value for the key 'dni'"}),
                    400,
                )
            person = json_util.dumps(mongo.db.people.find_one({DNI: dni}))
            if person != NULL:
                mongo.db.people.delete_one({DNI: dni})
                return "", 200
            else:
                return jsonify({"messege": "dni {} not found".format(dni)}), 204
        else:
            return "", 400


@app.route("/hora-arg")
def hora_arg():
    r = requests.get("http://worldtimeapi.org/api/timezone/ETC/UTC")
    date_utc_now = None
    if r.status_code == 200:
        date_utc_now = int(r.json()["unixtime"])
    else:
        date_utc_now = datetime.utcnow()
    time_formated_arg = (
        arrow.get(date_utc_now).to("GMT-3").format("DD/MM/YYYY HH:mm:ss")
    )
    return "{}".format(time_formated_arg), 200


if __name__ == "__main__":
    app.run(debug=True)
