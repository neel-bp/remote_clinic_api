from remote_clinic_api import db
from mongoengine import StringField
import json

class User(db.Document):
    email = StringField(required=True)
    first_name = StringField(max_length=50)
    last_name = StringField(max_length=50)

    def json(self):
        return json.dumps(
            {
                'email': self.email,
                'first_name': self.first_name,
                'last_name': self.last_name
            }
        )

