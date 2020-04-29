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
        return res

@app.route('/doctors/<id>', methods=['GET','PUT', 'DELETE'])
def doctors(id):
    if request.method == 'GET': ## Return Single Doctor.
        try: # Try to get doctor info with the given id. 
            result = Doctor.objects(id = id)
            jsonData = result.to_json()
            return jsonData
        except IndexError as notFound:
            return f'Record with the id: `{id}` is NOT FOUND!!!'
        except ValidationError as err:
            return err.message
    elif request.method == 'PUT': ## Update Doctor.
        try:
            body = request.json
            result = Doctor.objects(id = id)
            result[0].update(**body)
            return id
        except IndexError as notFound:
            return f'Record with the id: `{id}` is NOT FOUND!!!'
        except ValidationError as err:
            return err.message        
    elif request.method == 'DELETE': ## Delete Doctor.
        try:
            result = Doctor.objects(id = id)
            result[0].delete()
            return id
        except IndexError as notFound:
            return f'Record with the id: `{id}` is NOT FOUND!!!'
        except ValidationError as err:
            return err.message
    else:
        res = Response()
        res.status_code = 402
        return res
