from remote_clinic_api import db
from mongoengine import StringField
from marshmallow_mongoengine import ModelSchema

class User(db.Document):
    email = StringField(required=True)
    first_name = StringField(max_length=50)
    last_name = StringField(max_length=50)

class UserSchema(ModelSchema):
    class Meta:
        model = User

