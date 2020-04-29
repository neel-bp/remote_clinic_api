from remote_clinic_api import db
from mongoengine import StringField, EmailField, DateTimeField, BooleanField, DictField, FloatField, ReferenceField, EmbeddedDocument, EmbeddedDocumentField, EmbeddedDocumentListField
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
    image_path = StringField()
    signup_date = DateTimeField(default=datetime.utcnow)
    online = BooleanField()
    address = EmbeddedDocumentField(Address)


# defining schema for json serialization
class PatientSchema(ModelSchema):
    class Meta:
        model = Patient

class Reviews(db.Document):
    rating = FloatField(max_value=5)
    review_by = ReferenceField('Patient')
    # review_for = ReferenceField('Doctor') after Doctor class is created
    review_date = DateTimeField(default=datetime.utcnow)
    comment = StringField()

class ReviewsSchema(ModelSchema):
    class Meta:
        model = Reviews


class Drug(EmbeddedDocument):
    name = StringField()
    dose = StringField()
    time = StringField()
    description = StringField()

class DrugSchema(ModelSchema):
    class Meta:
        model = Drug

## patient prescriptions
class Prescription(db.Document):
    prescribed_by = StringField()
    #doctor_id = ReferenceField('Doctor') doctor id is used because if a user want to visit doctor page this id is used to find that doctor instead of doctor's name because name is aconflicting field multiple people can have same names
    notes = StringField()
    drugs = EmbeddedDocumentListField(Drug)
    prescription_date = DateTimeField(datetime.utcnow)
    prescribed_for = ReferenceField('Patient')

class PrescriptionSchema(ModelSchema):
    class Meta:
        model = Prescription

# patient interactions with doctors
class Interaction(db.Document):
    patient_id = ReferenceField('Patient')
    #doctor_id = ReferenceField('Doctor')
    doctor_name = StringField()
    medium = StringField()
    date = DateTimeField(default=datetime.utcnow)
    interaction_type = StringField() # didnt use type because type is a reserved word in python

class InteractionSchema(ModelSchema):
    class Meta:
        model = Interaction

class Reports(db.Document):
    title = StringField()
    report_type = StringField()
    description = StringField()
    issued_by_org = StringField()
    issued_date = DateTimeField(default=datetime.utcnow)
    file_path = StringField()
    report_of = ReferenceField('Patient')

class ReportSchema(ModelSchema):
    class Meta:
        model = Reports