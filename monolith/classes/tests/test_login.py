#test
from operator import contains
import requests
from sqlalchemy.sql.expression import true
from monolith.app import *

LOGIN_OK = 200
LOGIN_FAIL = 201
DOUBLE_LOGIN = 202

class TestCreate:

#1) login
    def test_login_user(self):
        app=create_app()
        with app.app_context():
            URL = 'http://127.0.0.1:5000/login'
            payload = {
                'email': 'email5',
                'password': 'pass5'
            }
            session = requests.session()
            r = requests.post(URL, data=payload, allow_redirects=True)
            assert r.status_code == LOGIN_OK

#2) wrong login
    def test_wrong_login_user(self):
        app=create_app()
        with app.app_context():
            URL = 'http://127.0.0.1:5000/login'
            payload = {
                'email': 'email5',
                'password': 'pass1000'
            }
            session = requests.session()
            r = requests.post(URL, data=payload)
            assert r.status_code == LOGIN_FAIL

#3) login when just login
    def test_login_user_when_just_login(self):
        app=create_app()
        with app.app_context():
            URL = 'http://127.0.0.1:5000/login'
            payload = {
                'email': 'email5',
                'password': 'pass5'
            }
            session = requests.session()
            r = requests.post(URL, data=payload)
            r = requests.post(URL)
            assert r.status_code == DOUBLE_LOGIN