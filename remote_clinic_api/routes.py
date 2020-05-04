from remote_clinic_api import app, db
from flask import jsonify, request, send_file, abort
from remote_clinic_api.models import *
import json

from flask import Response
from markupsafe import escape
from datetime import datetime
from mongoengine import ValidationError, FieldDoesNotExist, NotUniqueError

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

@app.route('/doctors/<doctorId>/documents', methods=['GET', 'POST'])
def ddocument(doctorId):
    if request.method == 'GET':
        try:
            document_list = []
            result = DDocuments.objects(owner = doctorId)  
            for i in result:
                document_list.append(DDocumentsSchema().dump(i))
            return jsonify(document_list)
        except ValidationError as err:
            return jsonify({'error':err.message})
    elif request.method == 'POST':
        body = request.json
        try: # Try to store info. 
            body.update({'owner':doctorId})
            ddocument = DDocumentsSchema().load(body)
            ddocument.save()
            return jsonify({"id": str(ddocument.id)})
        except FieldDoesNotExist as atterr:
            return jsonify({'error':f'incorrect structure, {atterr}'})
        except ValidationError as err:
            return jsonify({'error':err.message})
    else:
        res = Response()
        res.status_code = 402
        return res

@app.route('/doctors/<doctorId>/documents/<documentId>', methods=['GET','PUT', 'DELETE'])
def ddocuments(doctorId,documentId):
    if request.method == 'GET':
        try:
            result = DDocuments.objects.get_or_404(id = documentId, owner = doctorId)  
            jsonData = DDocumentsSchema().dump(result)
            return jsonify(jsonData)                        
        except ValidationError as err:
            return jsonify({'error':err.message})
    elif request.method == 'PUT':
        try:
            body = request.json
            result = DDocuments.objects.get_or_404(id = documentId, owner = doctorId)
            result = DDocumentsSchema().dump(result)
            result.update(body)
            result = DDocumentsSchema().load(result)
            result.save()
            return jsonify({"id": documentId, "owner": doctorId})
        except ValidationError as err:
            return jsonify({'error':err.message})
    elif request.method == 'DELETE':
        try:
            result = DDocuments.objects.get_or_404(id = documentId, owner = doctorId)  
            result.delete()
            return jsonify({"documentId":documentId,"ownerId":doctorId})
        except ValidationError as err:
            return jsonify({'error':err.message})
    else:
        res = Response()
        res.status_code = 402
        return res


@app.route('/doctors/<doctorId>/reviews', methods=['GET','POST'])
def docreviews(doctorId):
    if request.method == 'GET':
        try:
            doctor = Doctor.objects.get_or_404(id=str(doctorId))
            review_list = []
            result = Reviews.objects(review_for = doctor)  
            for i in result:
                review_list.append(ReviewsSchema().dump(i))
            return jsonify(review_list)            
        except ValidationError as err:
            return jsonify({'error':err.message})
    elif request.method == 'POST':
        body = request.json
        try: # Try to store info. 
            body['review_for'] = str(doctorId)
            review = ReviewsSchema().load(body)
            review.for_name = str(review.review_for.name)+' '+str(review.review_for.surname)
            review.save()
            return jsonify({"id": str(review.id)})
        except FieldDoesNotExist as atterr:
            return jsonify({'INCORRECT STRUCTURE': atterr})
        except ValidationError as error:
            return jsonify({'error':error.message})


@app.route('/doctors/<doctorId>/reviews/<reviewId>', methods=['GET','PUT', 'DELETE'])
def mod_docreviews(doctorId,reviewId):
    if request.method == 'GET':
        try:
            result = Reviews.objects.get_or_404(id = reviewId, review_for = doctorId)  
            jsonData = ReviewsSchema().dump(result)
            return jsonify(jsonData)                        
        except ValidationError as err:
            return jsonify({'error':err.message})
    elif request.method == 'PUT':
        try:
            body = request.json
            result = Reviews.objects.get_or_404(id = reviewId, review_for = doctorId)
            result = ReviewsSchema().dump(result)
            result.update(body)
            result = ReviewsSchema().load(result)
            result.save()
            return jsonify({"id": reviewId, "review_for": doctorId})
        except ValidationError as err:
            return jsonify({'error':err.message})        
    elif request.method == 'DELETE':
        try:
            result = Reviews.objects.get_or_404(id = reviewId, review_for = doctorId)  
            result.delete()
            return jsonify({"message":f'review {reviewId} has been successfully deleted'})
        except ValidationError as err:
            return jsonify({'error':err.message})


@app.route('/operators', methods=['GET','POST'])
def operator():
    if request.method == 'GET':
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
        
        result = Operator.objects[offset:end]
        jsonData = []
        for js in result:
            jsonData.append(OperatorSchema().dump(js))
        return jsonify(jsonData)
    elif request.method == 'POST':
        body = request.json
        try: 
            operator = OperatorSchema().load(body)
            operator.save()
            return jsonify({'id': str(operator.id) })
        except FieldDoesNotExist as atterr:
            return jsonify({'INCORRECT STRUCTURE': str(atterr)})
        except ValidationError as error:
            return jsonify({'error':error.message})
    else:
        res = Response()
        res.status_code = 401
        return res

@app.route('/operators/<id>', methods=['GET','PUT','DELETE'])
def get_operator(id):
    if request.method == 'GET':
        try: 
            result = Operator.objects.get_or_404(id = id)
            jsonData = OperatorSchema().dump(result)
            return jsonify(jsonData)
        except ValidationError as err:
            return jsonify({'error':err.message})
    elif request.method == 'PUT':
        try:
            body = request.json
            result = Operator.objects.get_or_404(id = id)
            result = OperatorSchema().dump(result)
            result.update(body)
            result = OperatorSchema().load(result)
            result.save()
            return jsonify({'message':f'operator {id} has been successfully updated'})
        except ValidationError as err:
            return jsonify({'error':err.message})        
    elif request.method == 'DELETE':
        try:
            result = Operator.objects.get_or_404(id = id)
            result.delete()
            return jsonify({'message':f'operator {id} has been successfully deleted'})
        except ValidationError as err:
            return jsonify({'error':err.message})
    else:
        res = Response()
        res.status_code = 401
        return res


@app.route('/operators/<operatorId>/roles', methods=['GET','POST'])
def operator_roles(operatorId):
    if request.method == 'GET':
        try:
            result = Operator.objects.get_or_404(id = operatorId)
            role_li = []
            roles = result.roles
            for i in roles:
                role_li.append({'id':str(i.id),'title':i.title})  
            return jsonify(role_li)            
        except ValidationError as err:
            return jsonify({'error':err.message})
    elif request.method == 'POST':
        body = request.json
        try: # Try to store info. 
            role = Roles.objects(title__icontains=body['role']).first()
            opRole = Operator.objects.get_or_404(id = operatorId)
            opRole.roles.append(role)
            opRole.save()
            return jsonify({'message':'role successfully added'})
        except FieldDoesNotExist as atterr:
            return jsonify({'error':atterr})
        except ValidationError as error:
            return jsonify({'error':error.message})
    else:
        res = Response()
        res.status_code = 401
        return res


@app.route('/operators/<operatorId>/roles/<roleId>', methods=['GET','DELETE'])
def get_operator_roles(operatorId, roleId):
    if request.method == 'GET':
        try:
            role = Roles.objects.get_or_404(id=roleId)
            result = Operator.objects.get_or_404(id = operatorId, roles__in=[role])  
            jsonData = OperatorSchema().dump(result)
            return jsonify(jsonData)
        except ValidationError as err:
            return err.message
    elif request.method == 'DELETE':
        try:
            role = Roles.objects.get_or_404(id=roleId)  
            operator = Operator.objects.get_or_404(id=operatorId, roles__in=[role])
            operator.roles.remove(role)
            operator.save()
            return jsonify({'message':f'role {roleId} successfully deleted'})
        except ValidationError as err:
            return jsonify({'error':err.message})
    else:
        res = Response()
        res.status_code = 401
        return res

@app.route('/operators/<operatorId>/permissions', methods=['GET'])
def operator_permission(operatorId):
    if request.method == 'GET':
        try:
            permissions = [] # Create empty permisstion List.
            operator = Operator.objects.get_or_404(id = operatorId)
            roles = operator.roles 
            for role in roles:
                for p in role.permissions:
                    permissions.append(p)
            return jsonify({'permissions':permissions})
        except AttributeError as atterr:
            return jsonify({'error':str(atterr)})                       
        except ValidationError as err:
            return jsonify({'error':err.message})
    else:
        res = Response()
        res.status_code = 401
        return res

#TODO: have to refactor following routes
@app.route('/roles', methods=['GET','POST'])
def roles():
    if request.method == 'GET':
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
        result = Roles.objects[offset:end]
        jsonData = result.to_json()
        return jsonData
    elif request.method == 'POST':
        body = request.json
        try: 
            role = Roles(**body)
            role.save()
            return jsonify({'id': str(role.id) })
        except ValidationError as error:
            return error.message
    else:
        res = Response()
        res.status_code = 401
        return res  
@app.route('/roles/<id>', methods=['GET','PUT','DELETE'])
def get_roles(id):
    if request.method == 'GET':
        try: 
            result = Roles.objects(id = id)
            jsonData = result.to_json()
            return jsonData
        except IndexError as notFound:
            return f'Record with the id: `{id}` is NOT FOUND!!!'
        except ValidationError as err:
            return err.message
    elif request.method == 'PUT':
        try:
            body = request.json
            result = Roles.objects(id = id)
            result[0].update(**body)
            return id
        except IndexError as notFound:
            return f'Record with the id: `{id}` is NOT FOUND!!!'
        except ValidationError as err:
            return err.message   
    elif request.method == 'DELETE':
        try:
            result = Roles.objects(id = id)
            result[0].delete()
            return id
        except IndexError as notFound:
            return f'Record with the id: `{id}` is NOT FOUND!!!'
        except ValidationError as err:
            return err.message
    else:
        res = Response()
        res.status_code = 401
        return res


# image routes
@app.route('/patients/<string:patient_id>/pic', methods=['GET','PUT','POST','PATCH','DELETE'])
def patient_pic(patient_id):
    if request.method == 'POST' or request.method == 'PUT' or request.method == 'PATCH':
        if 'file' not in request.files:
            return jsonify({'error':'no file part'})
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error':'no file selected'})
        patient = Patient.objects.get_or_404(id=patient_id)
        patient.image.replace(file)
        patient.save()
        return jsonify({'message':'image successfully uploaded'})
    
    elif request.method == 'GET':
        patient = Patient.objects.get_or_404(id=patient_id)
        try:
            return send_file(patient.image, attachment_filename=f'{patient.image.md5}.'+str(patient.image.format).lower())
        except AttributeError:
            abort(404)

    elif request.method == 'DELETE':
        try:
            patient = Patient.objects.get_or_404(id=patient_id)
            patient.image.delete()
            patient.save()
            return jsonify({'message':'image deleted successfully'})
        except Exception as e:
            return jsonify({'error':e})

@app.route('/doctors/<string:doctor_id>/pic', methods=['GET','PUT','POST','PATCH','DELETE'])
def doctor_pic(doctor_id):
    if request.method == 'POST' or request.method == 'PUT' or request.method == 'PATCH':
        if 'file' not in request.files:
            return jsonify({'error':'no file part'})
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error':'no file selected'})
        doctor = Doctor.objects.get_or_404(id=doctor_id)
        doctor.image.replace(file)
        doctor.save()
        return jsonify({'message':'image successfully uploaded'})
    
    elif request.method == 'GET':
        doctor = Doctor.objects.get_or_404(id=doctor_id)
        try:
            return send_file(doctor.image, as_attachment=True, attachment_filename=f'{doctor.image.md5}.'+str(doctor.image.format).lower())
        except AttributeError:
            abort(404)

    elif request.method == 'DELETE':
        try:
            doctor = Doctor.objects.get_or_404(id=doctor_pic)
            doctor.image.delete()
            doctor.save()
            return jsonify({'message':'image successfully deleted'})
        except Exception as e:
            return jsonify({'error':e})
