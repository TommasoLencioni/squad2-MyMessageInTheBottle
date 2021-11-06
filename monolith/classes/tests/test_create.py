#test
import requests
from sqlalchemy.sql.expression import true
from monolith.app import *

class TestCreate:

#1) new user
    def test_create_user(self):
        app=create_app()
        with app.app_context():
            URL = 'http://127.0.0.1:5000/create_user'
            payload = {
                'email': 'email5',
                'firstname': 'name5',
                'lastname': 'last5',
                'password': 'pass5',
                'date_of_birth': '1/01/2000',
                'nickname': 'nick5',
                'location': 'Pisa'
            }
            session = requests.session()
            r = requests.post(URL, data=payload)
            user_check=db.session.query(User).filter(User.email=='email5').first()
            assert user_check is not None

#2) new user with same email 
    def test_create_user_same_email(self):
        app=create_app()
        with app.app_context():
            URL = 'http://127.0.0.1:5000/create_user'
            payload = {
                'email': 'email5',
                'firstname': 'name',
                'lastname': 'last',
                'password': 'pass',
                'date_of_birth': '1/01/2000',
                'nickname': 'nick',
                'location': 'Pisa'
            }
            session = requests.session()
            r = requests.post(URL, data=payload, allow_redirects=False)
            #assert r.url == 'http://127.0.0.1:5000/create_user'
            assert r.status_code == 302

#3) new user with same nickname
    def test_create_user_same_nick(self):
        app=create_app()
        with app.app_context():
            URL = 'http://127.0.0.1:5000/create_user'
            payload = {
                'email': 'email',
                'firstname': 'name',
                'lastname': 'last',
                'password': 'pass',
                'date_of_birth': '1/01/2000',
                'nickname': 'nick',
                'location': 'Pisa'
            }
            session = requests.session()
            r = requests.post(URL, data=payload, allow_redirects=False)
            #assert r.url == 'http://127.0.0.1:5000/create_user'
            assert r.status_code == 302