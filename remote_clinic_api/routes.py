from remote_clinic_api import app, db
from remote_clinic_api.models import User
from flask import jsonify


@app.route('/niggas')
def niggas():
    return jsonify(User.objects)
