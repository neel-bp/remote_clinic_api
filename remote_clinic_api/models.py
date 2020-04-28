from remote_clinic_api import db
from mongoengine import StringField, EmailField, DateTimeField, BooleanField, DictField, FloatField, ReferenceField
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


# defining schema for json serialization
class PatientSchema(ModelSchema):
    class Meta:
        model = Patient

class Reviews(db.Document):
    rating = FloatField(max_value=5)
    review_by = ReferenceField('Patient')
    # review_for = ReferenceField(Doctor) after Doctor class is created
    review_date = DateTimeField(default=datetime.utcnow)
    comment = StringField()

class ReviewsSchema(ModelSchema):
    class Meta:
        model = Reviews