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

@app.route('/patients/<string:patient_id>', methods=['GET','PATCH','PUT','DELETE'])
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
    
    elif request.method == 'DELETE':
        patient_to_delete = Patient.objects.get_or_404(id=patient_id)
        patient_to_delete.delete()
        return jsonify({'message':f'{patient_id} patient has been successfully deleted'})

@app.route('/patients/<string:patient_id>/prescriptions',methods=['GET','POST'])
def get_prescriptions(patient_id):
    if request.method == 'GET':
        Prescription_objects = Prescription.objects(prescribed_for=str(patient_id))
        prescription_schema = PrescriptionSchema()
        pres_list = []
        for i in Prescription_objects:
            pres_list.append(prescription_schema.dump(i))
        return jsonify(pres_list)
    
    elif request.method == 'POST':
        pres_body = request.json
        pres_body['prescribed_for'] = str(patient_id)
        prescription = PrescriptionSchema().load(pres_body)
        prescription.save()
        return jsonify(PrescriptionSchema().dump(prescription))

@app.route('/patients/<string:patient_id>/prescriptions/<string:pres_id>', methods=['GET','DELETE','PUT','PATCH'])
def get_prescription(patient_id, pres_id):
    if request.method == 'GET':
        prescription = Prescription.objects.get_or_404(id=pres_id)
        return jsonify(PrescriptionSchema().dump(prescription))
    elif request.method == 'DELETE':
        prescription_to_delete = Prescription.objects.get_or_404(id=pres_id)
        prescription_to_delete.delete()
        return jsonify({'message':f'{pres_id} has been successfully deleted'})
    elif request.method == 'PUT' or request.method == 'PATCH':
        try:
            pres_body = request.json
            pres_dic = PrescriptionSchema().dump(Prescription.objects.get_or_404(id=str(pres_id)))
            pres_dic.update(pres_body)
            prescription_updated = PrescriptionSchema().load(pres_dic)
            prescription_updated.save()
            return jsonify({'message':f'{pres_id} has been successfully added'})
        except:
            return jsonify({'message':f'some error has occured'})



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
        doc_list = []
        for docs in result:
            doc_list.append(DoctorSchema().dump(docs))
        return jsonify(doc_list)
    elif request.method == 'POST': ## Add Doctor Record.
        body = request.json
        try: # Try to store doctor info. 
            doctor = DoctorSchema().load(body)
            doctor.save()
            return jsonify({'id': str(doctor.id) })
        except ValidationError as error:
            return jsonify({'error':error.message})
    else:
        res = Response()
        res.status_code = 402
        return res

# refactoring done, all serialization stuff applied
@app.route('/doctors/<id>', methods=['GET','PUT', 'DELETE'])
def doctors(id):
    if request.method == 'GET': ## Return Single Doctor.
        try: # Try to get doctor info with the given id. 
            result = Doctor.objects.get_or_404(id = id)
            jsonData = DoctorSchema().dump(result)
            return jsonify(jsonData)
        except ValidationError as err:
            return jsonify({'error':err.message})
    elif request.method == 'PUT': ## Update Doctor.
        try:
            body = request.json
            result = Doctor.objects.get_or_404(id=str(id))
            result_dic = DoctorSchema().dump(result)
            result_dic.update(body)
            updated_doctor = DoctorSchema().load(result_dic)
            updated_doctor.save()
            return jsonify({'message':'record updated successfully'})
        except ValidationError as err:
            return jsonify({'error':err.message})
    elif request.method == 'DELETE': ## Delete Doctor.
        try:
            result = Doctor.objects.get_or_404(id = id)
            result.delete()
            return jsonify({'message':f'{id} doctor deleted successfully'})
        except ValidationError as err:
            return jsonify({'error':err.message})
    else:
        res = Response()
        res.status_code = 402
        return res

#TODO: have to refactor and apply serialization to the following two routes
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
