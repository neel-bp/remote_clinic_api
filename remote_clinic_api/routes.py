from remote_clinic_api import app, db
from flask import jsonify, request
from remote_clinic_api.models import *
import json


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
