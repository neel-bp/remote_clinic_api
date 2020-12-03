import unittest
from remote_clinic_api import app
from db_helper import t_connection, db
from remote_clinic_api.models import *
from pyunitreport import HTMLTestRunner

class TestRemoteClinic(unittest.TestCase):
    app.config['TESTING'] = True
    test_client = app.test_client()

    def setUp(self):
        t_connection.drop_database('remote_clinic_test')

    def tearDown(self):
        t_connection.drop_database('remote_clinic_test')

    def test_if_api_is_working(self):
        response = self.test_client.get('/')
        self.assertEqual(200, response.status_code)

    def test_data_insertion(self):
        response = self.test_client.post('/patients', json={'username':'neelu','password':'graffhead'})
        self.assertEqual(200,response.status_code)
        patient = Patient.objects.first()
        self.assertEqual('neelu', patient.username)

    def test_json_format(self):
        """testing if data is coming in
        proper json format or not (serialization)"""
        self.test_client.post('/patients',json={'username':'neelu','password':'graffhead'})
        response = self.test_client.get('/patients')
        self.assertTrue(response.is_json)

    def test_password_encryption(self):
        self.test_client.post('/patients',json={'username':'neelu','password':'graffhead'})
        patient = Patient.objects(username='neelu').first()
        self.assertNotEqual('graffhead',patient.password)

    def test_get_all_patients_and_doctors(self):
        self.test_client.post('/patients',json={'username':'neelu','password':'graffhead'})
        self.test_client.post('/doctors',json={'username':'baba','password':'graffhead'})
        response = self.test_client.get('/patients')
        patient = response.get_json()[0]
        response_doc = self.test_client.get('/doctors')
        doc = response_doc.get_json()[0]
        self.assertIn('neelu',patient.values())
        self.assertIn('baba', doc.values())

    def test_get_patient_and_doctor_by_id(self):
        self.test_client.post('/patients',json={'username':'neelu','password':'graffhead'})
        self.test_client.post('/doctors',json={'username':'baba','password':'graffhead'})
        response = self.test_client.get('/patients')
        response_doc = self.test_client.get('/doctors')
        patient = response.get_json()[0]
        doctor = response_doc.get_json()[0]
        patient_dic = self.test_client.get(f'/patients/{patient["id"]}').get_json()
        doctor_dic = self.test_client.get(f'/doctors/{doctor["id"]}').get_json()
        self.assertIn('neelu',patient_dic.values())
        self.assertIn('baba', doctor_dic.values())

        

if __name__ == "__main__":
    unittest.main(testRunner=HTMLTestRunner(output='report'))
