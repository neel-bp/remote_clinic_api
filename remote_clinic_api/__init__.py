from flask import Flask
from flask_mongoengine import MongoEngine
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = '8f6e9db6d46e655086cb7bc18f754ae9'
app.config['MONGODB_DB'] = 'remote_clinic'
app.config['JWT_SECRET_KEY'] = '266c7d53e8e55c0f4db0ee85e59a7b9c'
db = MongoEngine(app)
jwt = JWTManager(app)
bcrypt = Bcrypt(app)

from remote_clinic_api import routes