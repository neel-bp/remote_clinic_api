from remote_clinic_api import db
from mongoengine import StringField, EmailField, DateTimeField, BooleanField, DictField, EmbeddedDocument, EmbeddedDocumentField, Document, FloatField, ReferenceField, ObjectIdField  


from marshmallow_mongoengine import ModelSchema
from datetime import datetime

class Patient(db.Document):
    name = StringField()
    surname = StringField()
    email = EmailField()
    phone = StringField()
    gender = StringField()
    address = StringField()
    image_path = StringField()
    signup_date = DateTimeField(default=datetime.utcnow)
    online = BooleanField()
    reviews = DictField()

# defining schema for json serialization
class PatientSchema(ModelSchema):
    class Meta:
        model = Patient



class Address(EmbeddedDocument):
    country = StringField(),
    city = StringField(),
    street = StringField(),

class Doctor(Document):
    name = StringField()
    surname = StringField()
    email = EmailField()
    phone = StringField()
    gender = StringField()
    address = EmbeddedDocumentField(Address)
    image_path = StringField()
    signup_date = DateTimeField(default=datetime.utcnow)
    online = BooleanField()
    specilization = StringField()
    about = StringField()
    experience = StringField()
    pmdc_verified = BooleanField()
    pmdc_reg_num = StringField()
    verification_status = StringField()
    verified_by = ObjectIdField()
    verification_date = DateTimeField()

# defining schema for json serialization
class DoctorSchema(ModelSchema):
    class Meta:
        model = Doctor

class DDocuments(Document):
    owner: ObjectIdField()
    title: StringField()
    type_ = StringField()
    description = StringField()
    issued_by_org = StringField()
    issued_date = DateTimeField()
    img_path = StringField(),
    verification_status = StringField(),
    verified_by = ObjectIdField(),
    verification_date = DateTimeField(),
    rejection_cause = StringField()

# defining schema for json serialization
class DDcoumentsSchema(ModelSchema):
    class Meta:
        model = DDocuments

class Operator(Document):
    name = StringField()
    surname = StringField()
    phone = StringField()
    dob = DateTimeField()
    email = EmailField()
    address = EmbeddedDocumentField(Address)
    password = StringField()
    doj = DateTimeField()


# defining schema for json serialization
class OperatorSchema(ModelSchema):
    class Meta:
        model = Operator
