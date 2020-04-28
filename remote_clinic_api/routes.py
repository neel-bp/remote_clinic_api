from remote_clinic_api import app, db
from remote_clinic_api.models import User, UserSchema
from flask import jsonify


@app.route('/niggas')
def niggas():
    li=[]
    user_schema = UserSchema()
    for i in User.objects:
        li.append(user_schema.dump(i))
    return jsonify(li)
