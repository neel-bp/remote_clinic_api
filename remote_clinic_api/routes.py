from remote_clinic_api import app, db
from flask import jsonify
from flask import request
from flask import Response
from markupsafe import escape
import json
from remote_clinic_api.models import Doctor, Address
from datetime import datetime
from mongoengine import ValidationError

@app.route('/')
def hello():
    return jsonify({'hello':'world'})

@app.route('/doctors', methods=['GET', 'POST'])
def doctor():
    if request.method == 'GET': ## Return All Doctors List. 
        result = Doctor.objects() # Query all the objects.
        jsonData = result.to_json()
        return jsonData
    elif request.method == 'POST': ## Add Doctor Record.
        body = request.json
        try: # Try to store doctor info. 
            doctor = Doctor(**body)
            doctor.save()
            return jsonify({'id': str(doctor.id) })
        except ValidationError as error:
            return error.message
    else:
        res = Response()
        res.status_code = 402
        res.status = "Bad Request: Action Not Defined"
        return res

@app.route('/doctors/<id>', methods=['GET','PUT', 'DELETE'])
def doctors(id):
    if request.method == 'GET': ## Return Single Doctor.
        return jsonify({'method': 'GET','route': '/doctor/<id>','param': id})
    elif request.method == 'PUT': ## Update Doctor.
        return jsonify({'method': 'PUT','route': '/doctor/<id>','param': id})
    elif request.method == 'DELETE': ## Delete Doctor.
        return jsonify({'method': 'DELETE','route': '/doctor/<id>','param': id})
    else:
        return "405: Invalid Request Type."
