from remote_clinic_api import app, db, jwt, bcrypt
from flask import jsonify, request, send_file, abort, make_response
from remote_clinic_api.models import *
import json

from flask import Response
from markupsafe import escape
from datetime import datetime
from mongoengine import ValidationError, FieldDoesNotExist, NotUniqueError
from marshmallow.exceptions import ValidationError as MValidationError
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity


@app.route('/')
def hello():
    return jsonify({'hello':'world'})

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': '404 Not found'}), 404)

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
        password = patient.password
        patient.password = bcrypt.generate_password_hash(password).decode('utf-8')
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
        old_patient = Patient.objects.get_or_404(id = str(patient_id))
        old_patient_image = old_patient.image
        patient_dic = PatientSchema().dump(Patient.objects.get_or_404(id=str(patient_id)))
        patient_dic.update(updated_fields)
        updated_patient = PatientSchema().load(patient_dic)
        updated_patient.image = old_patient_image
        updated_patient.save()
        return jsonify(PatientSchema().dump(updated_patient))
    
    elif request.method == 'DELETE':
        patient_to_delete = Patient.objects.get_or_404(id=patient_id)
        patient_to_delete.delete()
        return jsonify({'message':f'{patient_id} patient has been successfully deleted'})

@app.route('/patients/<string:patient_id>/prescriptions',methods=['GET','POST'])
def get_prescriptions(patient_id):
    if request.method == 'GET':
        appointmentId = request.args.get('appointmentId')
        if appointmentId is not None:
            Prescription_objects = Prescription.objects(prescribed_for=str(patient_id),appointmentId = str(appointmentId))
        else:
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
            password = doctor.password
            doctor.password = bcrypt.generate_password_hash(password).decode('utf-8')
            doctor.save()
            return jsonify({'id': str(doctor.id) })
        except ValidationError as error:
            return jsonify({'error':error.message})
        except MValidationError as err:
            return jsonify({'error': err.messages})
    else:
        res = Response()
        res.status_code = 402
        return res

# refactoring done, all serialization stuff applied
@app.route('/doctors/<id>', methods=['GET','PUT', 'PATCH', 'DELETE'])
def doctors(id):
    if request.method == 'GET': ## Return Single Doctor.
        try: # Try to get doctor info with the given id. 
            result = Doctor.objects.get_or_404(id = id)
            jsonData = DoctorSchema().dump(result)
            return jsonify(jsonData)
        except ValidationError as err:
            return jsonify({'error':err.message})
    elif request.method == 'PUT' or request.method == 'PATCH': ## Update Doctor.
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
        except MValidationError as err:
            return jsonify({'error': err.messages})
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

# routes for displaying all document routes regardless of doctor
@app.route('/documents', methods=['GET'])
def documents_list():
    try:
        document_list = []
        result = DDocuments.objects  
        for i in result:
            document_list.append(DDocumentsSchema().dump(i))
        return jsonify(document_list)
    except ValidationError as err:
        return jsonify({'error':err.message})

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
        except MValidationError as err:
            return jsonify({'error': err.messages})
    else:
        res = Response()
        res.status_code = 402
        return res

@app.route('/doctors/<doctorId>/documents/<documentId>', methods=['GET','PUT', 'PATCH', 'DELETE'])
def ddocuments(doctorId,documentId):
    if request.method == 'GET':
        try:
            result = DDocuments.objects.get_or_404(id = documentId, owner = doctorId)  
            jsonData = DDocumentsSchema().dump(result)
            return jsonify(jsonData)                        
        except ValidationError as err:
            return jsonify({'error':err.message})
    elif request.method == 'PUT' or request.method == 'PATCH':
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
        except MValidationError as err:
            return jsonify({'error': err.messages})
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
        except MValidationError as err:
            return jsonify({'error': err.messages})


@app.route('/doctors/<doctorId>/reviews/<reviewId>', methods=['GET','PUT','PATCH', 'DELETE'])
def mod_docreviews(doctorId,reviewId):
    if request.method == 'GET':
        try:
            result = Reviews.objects.get_or_404(id = reviewId, review_for = doctorId)  
            jsonData = ReviewsSchema().dump(result)
            return jsonify(jsonData)                        
        except ValidationError as err:
            return jsonify({'error':err.message})
    elif request.method == 'PUT' or request.method == 'PATCH':
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
        except MValidationError as err:
            return jsonify({'error': err.messages})
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
        except MValidationError as err:
            return jsonify({'error': err.messages})
    else:
        res = Response()
        res.status_code = 401
        return res

@app.route('/operators/<id>', methods=['GET','PUT', 'PATCH', 'DELETE'])
def get_operator(id):
    if request.method == 'GET':
        try: 
            result = Operator.objects.get_or_404(id = id)
            jsonData = OperatorSchema().dump(result)
            return jsonify(jsonData)
        except ValidationError as err:
            return jsonify({'error':err.message})
    elif request.method == 'PUT' or request.method == 'PATCH':
        try:
            body = request.json
            result = Operator.objects.get_or_404(id = id)
            old_image = result.image
            result = OperatorSchema().dump(result)
            result.update(body)
            result = OperatorSchema().load(result)
            result.image = old_image
            result.save()
            return jsonify({'message':f'operator {id} has been successfully updated'})
        except ValidationError as err:
            return jsonify({'error':err.message})        
        except MValidationError as err:
            return jsonify({'error': err.messages})
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
        jsonData=[]
        for role in result:
            jsonData.append(RolesSchema().dump(role))
        return jsonify(jsonData)
    elif request.method == 'POST':
        body = request.json
        try: 
            role = RolesSchema().load(body)
            role.save()
            return jsonify({'id':str(role.id)})
        except ValidationError as error:
            return jsonify({'error':error.message})
        except MValidationError as err:
            return jsonify({'error': err.messages})
    else:
        res = Response()
        res.status_code = 401
        return res  
@app.route('/roles/<id>', methods=['GET','PUT', 'PATCH', 'DELETE'])
def get_roles(id):
    if request.method == 'GET':
        try: 
            result = Roles.objects.get_or_404(id = id)
            jsonData = RolesSchema().dump(result)
            return jsonify(jsonData)
        except ValidationError as err:
            return jsonify({'error':err.message})
    elif request.method == 'PUT' or request.method == 'PATCH':
        try:
            body = request.json
            result = Roles.objects.get_or_404(id = id)
            result = RolesSchema().dump(result)
            result.update(body)
            result = RolesSchema().load(result)
            result.save()
            return jsonify({'message':f'role {id} has been updated successfully'})
        except ValidationError as err:
            return jsonify({'error':err.message})
        except MValidationError as err:
            return jsonify({'error': err.messages})
    elif request.method == 'DELETE':
        try:
            result = Roles.objects.get_or_404(id = id)
            result.delete()
            return jsonify({'message':f'role {id} has been successfully deleted'})
        except ValidationError as err:
            return jsonify({'error':err.message})
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
            return send_file(doctor.image, attachment_filename=f'{doctor.image.md5}.'+str(doctor.image.format).lower())
        except AttributeError:
            abort(404)

    elif request.method == 'DELETE':
        try:
            doctor = Doctor.objects.get_or_404(id=doctor_id)
            doctor.image.delete()
            doctor.save()
            return jsonify({'message':'image successfully deleted'})
        except Exception as e:
            return jsonify({'error':e})

@app.route('/documents/<string:document_id>/pic',methods=['GET','POST','PUT','PATCH','DELETE'])
def document_pic(document_id):
    if request.method == 'POST' or request.method == 'PUT' or request.method == 'PATCH':
        if 'file' not in request.files:
            return jsonify({'error':'no file part'})
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error':'no file selected'})
        document = DDocuments.objects.get_or_404(id=document_id)
        document.image.replace(file)
        document.save()
        return jsonify({'message':'image successfully uploaded'})
    
    elif request.method == 'GET':
        document = DDocuments.objects.get_or_404(id=document_id)
        try:
            return send_file(document.image, attachment_filename=f'{document.image.md5}.'+str(document.image.format).lower())
        except AttributeError:
            abort(404)

    elif request.method == 'DELETE':
        try:
            document = DDocuments.objects.get_or_404(id=document_id)
            document.image.delete()
            document.save()
            return jsonify({'message':'image successfully deleted'})
        except Exception as e:
            return jsonify({'error':e})

# authentication routes
@app.route('/patients/auth', methods=['POST'])
def patient_login():
    if not request.is_json:
        return jsonify({'error':'missing or invalid JSON'}), 400
    try:
        username = str(request.json['username'])
        password = str(request.json['password'])
    except KeyError:
        return jsonify({'error':'no username or password key in request'}), 400
    if not username:
        return jsonify({'error':'missing username part'}), 400
    if not password:
        return jsonify({'error':'missing password part'}), 400
    patient = Patient.objects(username=username).first()
    if patient is None:
        return jsonify({'error':'no account with that username found'}), 400
    patient_username = patient.username
    patient_password_hash = patient.password
    if bcrypt.check_password_hash(patient_password_hash, password) == False:
        return jsonify({'error':'wrong username or password'}), 401
    
    access_token = create_access_token(identity=patient_username)
    return jsonify({'access_token':access_token, 'id':str(patient.id)})

@app.route('/doctors/auth', methods=['POST'])
def doctor_login():
    if not request.is_json:
        return jsonify({'error':'missing or invalid JSON'}), 400
    try:
        email = str(request.json['email'])
        password = str(request.json['password'])
    except KeyError:
        return jsonify({'error':'no email or password key in request'}), 400
    if not email:
        return jsonify({'error':'missing email part'}), 400
    if not password:
        return jsonify({'error':'missing password part'}), 400
    doctor = Doctor.objects(email=email).first()
    if doctor is None:
        return jsonify({'error':'no account with that email found'}), 400
    doctor_email = doctor.email
    doctor_password_hash = doctor.password
    if bcrypt.check_password_hash(doctor_password_hash, password) == False:
        return jsonify({'error':'wrong username or password'}), 401
    
    access_token = create_access_token(identity=doctor_email)
    return jsonify({'access_token':access_token, 'id':str(doctor.id)})

# Load api keys...
import json
with open('./remote_clinic_api/secret/vidyo.io.json', 'r') as j:
    data = json.load(j)
    
appName = data['appName']
appId = data['appId']
apiKey = data['apiKey']

import base64
from remote_clinic_api.GenerateToken import Token 

# Route for generating token
@app.route('/video/auth', methods=['POST'])
def video_chat_token():
    if not request.is_json:
        return jsonify({'error':'missing or invalid JSON'}), 400
    try:
        id = str(request.json['id'])
        userName = str(request.json['username'])
    except KeyError:
        return jsonify({'error':'no id or username key in request'}), 400
    if not id:
        return jsonify({'error':'id id part'}), 400
    if not userName:
        return jsonify({'error':'missing username part'}), 400

    # TODO: Valadating user credentials or validate it using middleware

    token = Token(key=apiKey, appID=appId,userName=userName,vCardFile=None, expires=60 * 10)
    serialized = token.serialize()
    b64 = base64.b64encode(serialized)

    return jsonify({'token':b64.decode()})

# Appointment Route Handler...

# [CREATE] and [GET ALL] ROUTE Handler
@app.route('/appointments', methods=['GET', 'POST'])
def appointment_data():
    if request.method == 'GET': ## Return All Data.
        limit = request.args.get('limit') # ?limit=Number
        offset = request.args.get('offset') # ?offset=Number
        doctorId = request.args.get('doctorId') # ?doctorId=ObjectId
        patientId = request.args.get('patientId') # ?patientId=ObjectId
        try:
            if limit is not None: limit = int(limit)
            if offset is not None: offset = int(offset)

            if offset is None: end = limit
            elif limit is None: end = None 
            else: end = limit + offset

        except TypeError as ve:
            end = None
            offset = None

        if patientId is not None and doctorId is not None: # Both are provided.
            result = Appointment.objects(patientId=patientId,doctorId=doctorId)[offset:end]
        elif patientId is not None: # Patient Id is provided.
            result = Appointment.objects(patientId=patientId)[offset:end]
        elif doctorId is not None: # Doctor Id is provided.
            result = Appointment.objects(doctorId=doctorId)[offset:end]
        else: # None of is provided.
            result = Appointment.objects()[offset:end]
        r_list = []
        for appoint in result:
            r_list.append(AppointmentSchema().dump(appoint))
        return jsonify(r_list)
    elif request.method == 'POST': ## Add Record.
        body = request.json
        try: # Try to store info. 
            appointment = AppointmentSchema().load(body)
            appointment.save()
            return jsonify({'id': str(appointment.id) })
        except ValidationError as error:
            return jsonify({'error':error.message})
        except MValidationError as err:
            return jsonify({'error': err.messages})
    else:
        res = Response()
        res.status_code = 402
        return res

# [GET] [UPDATE] [DELETE] Route Handler
@app.route('/appointments/<id>', methods=['GET','PUT', 'PATCH' ,'DELETE'])
def modify_appointment_data(id):
    if request.method == 'GET':
        try: 
            result = Appointment.objects.get_or_404(id = id)
            jsonData = AppointmentSchema().dump(result)
            return jsonify(jsonData)
        except ValidationError as err:
            return jsonify({'error':err.message})
    elif request.method == 'PUT' or request.method == 'PATCH':
        try:
            body = request.json
            result = Appointment.objects.get_or_404(id = id)
            result = AppointmentSchema().dump(result)
            result.update(body)
            result = AppointmentSchema().load(result)
            result.save()
            return jsonify({'message':f'appointment {id} has been successfully updated'})
        except ValidationError as err:
            return jsonify({'error':err.message})        
        except MValidationError as err:
            return jsonify({'error': err.messages})
    elif request.method == 'DELETE':
        try:
            result = Appointment.objects.get_or_404(id = id)
            result.delete()
            return jsonify({'message':f'appointment {id} has been successfully deleted'})
        except ValidationError as err:
            return jsonify({'error':err.message})
    else:
        res = Response()
        res.status_code = 401
        return res
        