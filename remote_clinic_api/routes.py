from remote_clinic_api import app, db
from flask import jsonify, request
from remote_clinic_api.models import *
import json

from flask import Response
from markupsafe import escape
from datetime import datetime
from mongoengine import ValidationError, FieldDoesNotExist

@app.route('/')
def hello():
    return jsonify({'hello':'world'})

@app.route('/patients', methods = ['GET','POST'])
def patients():
    if request.method == 'GET':    
        patient_objects = Patient.objects.exclude('password')
        patient_schema = PatientSchema()
        p_list_json = []
        if request.args.get('limit') is not None:
            limit = request.args.get('limit')
            for i in patient_objects[:int(limit)]:
                p_list_json.append(patient_schema.dump(i))
        else:
            for j in patient_objects:
                p_list_json.append(patient_schema.dump(j))
        return jsonify(p_list_json)
    
    elif request.method == 'POST':
        patient_json = request.json
        patient_schema = PatientSchema()
        patient = patient_schema.load(patient_json)
        patient.save()
        new_patient = patient_schema.dump(patient)
        return jsonify(new_patient)

@app.route('/patients/<string:patient_id>', methods=['GET','PATCH','PUT'])
def get_patient(patient_id):
    if request.method == 'GET':
        patient_object = Patient.objects.exclude('password').get_or_404(id=str(patient_id))
        patient_schema = PatientSchema()
        return jsonify(patient_schema.dump(patient_object))

    elif request.method == 'PATCH' or request.method == 'PUT':
        updated_fields = request.json
        patient_dic = PatientSchema().dump(Patient.objects.get_or_404(id=str(patient_id)))
        patient_dic.update(updated_fields)
        updated_patient = PatientSchema().load(patient_dic)
        updated_patient.save()
        return jsonify(PatientSchema().dump(updated_patient))
@app.route('/doctors', methods=['GET', 'POST'])
def doctor():
    if request.method == 'GET': ## Return All Doctors List.
        limit = request.args.get('limit')
        offset = request.args.get('offset')
        try:
            if limit is not None: limit = int(limit)
            if offset is not None: offset = int(offset)

            if offset is None: end = limit
            elif limit is None: end = None 
            else: end = limit + offset

        except TypeError as ve:
            end = None
            offset = None
        result = Doctor.objects[offset:end]
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

@app.route('/doctors/<doctorId>/documents', methods=['GET', 'POST'])
def ddocument(doctorId):
    if request.method == 'GET':
        try:
            result = DDocuments.objects(owner = doctorId)  
            jsonData = result.to_json()
            return jsonData
        except IndexError as notFound:
            return f'Record with the id: `{doctorId}` is NOT FOUND!!!'            
        except ValidationError as err:
            return err.message
    elif request.method == 'POST':
        body = request.json
        try: # Try to store info. 
            ddocument = DDocuments(**body)
            ddocument.save()
            return jsonify({"id": str(ddocument.id)})
        except FieldDoesNotExist as atterr:
            return f"INCORRECT STRUCTURE: {str(atterr)}"
        except ValidationError as error:
            return error.message
    else:
        res = Response()
        res.status_code = 402
        return res

@app.route('/doctors/<doctorId>/documents/<documentId>', methods=['GET','PUT', 'DELETE'])
def ddocuments(doctorId,documentId):
    if request.method == 'GET':
        try:
            result = DDocuments.objects(id = documentId, owner = doctorId)  
            jsonData = result.to_json()
            return jsonData
        except IndexError as notFound:
            return f'Record with given id: `{documentId}` is NOT FOUND!!!'                        
        except ValidationError as err:
            return err.message
    elif request.method == 'PUT':
        try:
            body = request.json
            result = DDocuments.objects(id = documentId, owner = doctorId)
            result[0].update(**body)
            return jsonify({"id": documentId, "owner": doctorId})
        except IndexError as notFound:
            return f'Record with the id: `{id}` is NOT FOUND!!!'
        except ValidationError as err:
            return err.message        
    elif request.method == 'DELETE':
        try:
            result = DDocuments.objects(id = documentId, owner = doctorId)  
            result[0].delete()
            return jsonify({"documentId":documentId,"ownerId":doctorId})
        except ValidationError as err:
            return err.message
    else:
        res = Response()
        res.status_code = 402
        return res
