from remote_clinic_api import app, db
from flask import jsonify


@app.route('/')
def hello():
    return jsonify({'hello':'world'})
