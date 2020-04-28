from remote_clinic_api import db
from mongoengine import StringField, EmailField, DateTimeField, BooleanField, DictField
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
