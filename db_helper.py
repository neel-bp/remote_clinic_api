from remote_clinic_api import db

db.disconnect()
t_connection = db.connect('remote_clinic_test')