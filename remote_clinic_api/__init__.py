from flask import Flask
from flask_mongoengine import MongoEngine

app = Flask(__name__)
app.config['SECRET_KEY'] = '8f6e9db6d46e655086cb7bc18f754ae9'
app.config['MONGODB_DB'] = 'remote_clinic' 
db = MongoEngine(app)

from remote_clinic_api import routes