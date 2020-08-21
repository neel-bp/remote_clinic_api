from remote_clinic_api import db
from mongoengine import StringField, EmailField, DateTimeField, BooleanField, DictField, EmbeddedDocument, EmbeddedDocumentField, Document, FloatField, ReferenceField, ObjectIdField, EmbeddedDocumentListField, GenericReferenceField, ListField, ImageField


from marshmallow_mongoengine import ModelSchema
from datetime import datetime

class Address(EmbeddedDocument):
    latitude = FloatField()
    longitude = FloatField()
    country = StringField()
    city = StringField()
    street = StringField()

class AddressSchema(ModelSchema):
    class Meta:
        model = Address

class Patient(db.Document):
    username = StringField()
    password = StringField()
    name = StringField()
    surname = StringField()
    email = EmailField()
    phone = StringField()
    gender = StringField()
    image = ImageField()
    signup_date = DateTimeField(default=datetime.utcnow)
    online = BooleanField(default=False)
    address = EmbeddedDocumentField(Address)


# defining schema for json serialization
class PatientSchema(ModelSchema):
    class Meta:
        model = Patient




class Drug(EmbeddedDocument):
    name = StringField()
    d_type = StringField()
    dose = StringField()
    time = StringField()
    for_days = StringField()
    description = StringField()

class DrugSchema(ModelSchema):
    class Meta:
        model = Drug



class Reports(db.Document):
    title = StringField()
    report_type = StringField()
    description = StringField()
    issued_by_org = StringField()
    issued_date = DateTimeField(default=datetime.utcnow)
    Image = ImageField()
    report_of = ReferenceField('Patient')

class ReportSchema(ModelSchema):
    class Meta:
        model = Reports

# Note: One Role can have multiple permissions: one to many relationship
# Note: When creating new Role permissions should be already defined.
class Roles(db.Document):
    title = StringField(required=True)
    permissions = ListField(StringField(), required=True) # List of permissions


# defining schema for json serialization
class RolesSchema(ModelSchema):
    class Meta:
        model = Roles


class Operator(db.Document):
    name = StringField()
    surname = StringField()
    phone = StringField()
    dob = DateTimeField()
    email = EmailField()
    address = EmbeddedDocumentField(Address)
    password = StringField()
    doj = DateTimeField()
    roles = ListField(ReferenceField('Roles'))


# defining schema for json serialization
class OperatorSchema(ModelSchema):
    class Meta:
        model = Operator


class Doctor(db.Document):
    name = StringField(max_length=255)
    surname = StringField(max_length=255)
    email = EmailField()
    username = StringField()
    password = StringField()
    tags = ListField(StringField()) # List of String TAGS 
    phone = StringField(max_length=255)
    gender = StringField(max_length=32)
    address = EmbeddedDocumentField(Address)
    image = ImageField()
    signup_date = DateTimeField(default=datetime.utcnow)
    online = BooleanField(default=False)
    specialization = StringField(max_length=255)
    about = StringField(max_length=255)
    experience = StringField()
    pmdc_verified = BooleanField(default=False)
    pmdc_reg_num = StringField()
    verification_status = StringField(default='Pending')
    verified_by = ReferenceField('Operator')
    verification_date = DateTimeField()

    meta = {
        'indexes':['$name']
    }

# defining schema for json serialization
class DoctorSchema(ModelSchema):
    class Meta:
        model = Doctor


# patient interactions with doctors
class Interaction(db.Document):
    patient_id = ReferenceField('Patient')
    doctor_id = ReferenceField('Doctor')
    doctor_name = StringField()
    medium = StringField()
    date = DateTimeField(default=datetime.utcnow)
    interaction_type = StringField() # didnt use type because type is a reserved word in python

class InteractionSchema(ModelSchema):
    class Meta:
        model = Interaction



class DDocuments(db.Document):
    owner = ReferenceField('Doctor')
    owner_name = StringField()
    title = StringField(max_length=255)
    document_type = StringField(max_length=64)
    description = StringField(max_length=255)
    issued_by_org = StringField(max_length=255)
    issued_date = DateTimeField(default=datetime.utcnow)
    image = ImageField()
    verification_status = StringField(default='Pending')
    verified_by = ReferenceField('Operator')
    verification_date = DateTimeField()
    rejection_cause = StringField()

# defining schema for json serialization
class DDocumentsSchema(ModelSchema):
    class Meta:
        model = DDocuments  

class Reviews(db.Document):
    rating = FloatField(max_value=5)
    review_by = ObjectIdField() # Reviewer could be any
    reviewer_name = StringField(max_length=255)
    review_for = ReferenceField('Doctor') # Reviewed For could be any
    for_name = StringField(max_length=255)
    review_date = DateTimeField(default=datetime.utcnow)
    comment = StringField()

class ReviewsSchema(ModelSchema):
    class Meta:
        model = Reviews


class Appointment(db.Document):
    patientId = ReferenceField('Patient')
    doctorId = ReferenceField('Doctor')
    patientName = StringField(max_length=255)
    doctorName = StringField(max_length=255)
    patientAvatar = StringField()
    doctorAvatar = StringField()
    appTime = StringField(max_length=255)
    appDate = StringField(max_length=255) 
    createdOn = DateTimeField(default=datetime.utcnow)
    token = StringField()
    status = StringField(max_length=255, default='Pending')
    duration = StringField(max_length=255)

class AppointmentSchema(ModelSchema):
    class Meta:
        model = Appointment

## patient prescriptions
class Prescription(db.Document):
    prescribed_by = ReferenceField('Doctor')
    appointmentId = ReferenceField('Appointment')
    notes = StringField()
    drugs = EmbeddedDocumentListField(Drug)
    prescription_date = DateTimeField(datetime.utcnow)
    prescribed_for = ReferenceField('Patient')

class PrescriptionSchema(ModelSchema):
    class Meta:
        model = Prescription



