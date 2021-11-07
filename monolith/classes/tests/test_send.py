#test 
from operator import contains
import requests
from sqlalchemy.sql.expression import true
from monolith.app import *
from monolith.database import BlackList, Message

class TestCreate_send:

#1) send email
    def test_send_email(self):
        app=create_app()
        with app.app_context():
            URL_login = 'http://127.0.0.1:5000/login'
            payload_login = {
                'email': 'email5',
                'password': 'pass5'
            }
            session_login = requests.session()
            r_login = requests.post(URL_login, data=payload_login)
            loginCookies = r_login.cookies
            URL = 'http://127.0.0.1:5000/send'
            payload = {
                'recipient': 'nick1',
                'body': 'ciao nick1',
                'delivery_date': '7/11/2021',
                'submit_button': 'Send',
            }
            file = {'image_file': ''}
            session = requests.session()
            r = requests.post(URL, files=file, cookies=loginCookies, data=payload)
            nick5 = db.session.query(User).filter(User.nickname=="nick5").first()
            nick1 = db.session.query(User).filter(User.nickname=="nick1").first()
            message_check=db.session.query(Message).filter(Message.receiver_id==nick1.id).filter(Message.sender_id==nick5.id).filter(Message.body=="ciao nick1").first()
            assert message_check is not None

#2) send email to multiple user
    def test_send_email_multiple_users(self):
        app=create_app()
        with app.app_context():
            URL_login = 'http://127.0.0.1:5000/login'
            payload_login = {
                'email': 'email5',
                'password': 'pass5'
            }
            session_login = requests.session()
            r_login = requests.post(URL_login, data=payload_login)
            loginCookies = r_login.cookies
            URL = 'http://127.0.0.1:5000/send'
            payload = {
                'recipient': ['nick1','nick2'],
                'body' : 'ciao nick1 e nick2',
                'delivery_date': '7/11/2021',
                'submit_button': 'Send',
            }
            file = {'image_file': ''}
            session = requests.session()
            r = requests.post(URL, files=file, cookies=loginCookies, data=payload)
            nick5 = db.session.query(User).filter(User.nickname=="nick5").first()
            nick1 = db.session.query(User).filter(User.nickname=="nick1").first()
            nick2 = db.session.query(User).filter(User.nickname=="nick2").first()
            message_check_nick1=db.session.query(Message).filter(Message.receiver_id==nick1.id).filter(Message.sender_id==nick5.id).filter(Message.body=="ciao nick1 e nick2").first()
            message_check_nick2=db.session.query(Message).filter(Message.receiver_id==nick2.id).filter(Message.sender_id==nick5.id).filter(Message.body=="ciao nick1 e nick2").first()
            assert message_check_nick1 is not None and message_check_nick2 is not None

#3) draft email
    def test_draft_email(self):
        app=create_app()
        with app.app_context():
            URL_login = 'http://127.0.0.1:5000/login'
            payload_login = {
                'email': 'email5',
                'password': 'pass5'
            }
            session_login = requests.session()
            r_login = requests.post(URL_login, data=payload_login)
            loginCookies = r_login.cookies
            URL = 'http://127.0.0.1:5000/send'
            payload = {
                'recipient': 'nick1',
                'body': 'ciao draft nick1',
                'delivery_date': '7/11/2021',
                'submit_button': 'Save as draft',
            }
            file = {'image_file': ''}
            session = requests.session()
            r = requests.post(URL, files=file, cookies=loginCookies, data=payload)
            nick5 = db.session.query(User).filter(User.nickname=="nick5").first()
            nick1 = db.session.query(User).filter(User.nickname=="nick1").first()
            message_check=db.session.query(Message).filter(Message.receiver_id==nick1.id).filter(Message.sender_id==nick5.id).filter(Message.body=="ciao draft nick1").filter(Message.is_draft==True).first()
            assert message_check is not None

#4) draft email to multiple users
    def test_draft_email_multiple_users(self):
        app=create_app()
        with app.app_context():
            URL_login = 'http://127.0.0.1:5000/login'
            payload_login = {
                'email': 'email5',
                'password': 'pass5'
            }
            session_login = requests.session()
            r_login = requests.post(URL_login, data=payload_login)
            loginCookies = r_login.cookies
            URL = 'http://127.0.0.1:5000/send'
            payload = {
                'recipient': ['nick1','nick2'],
                'body' : 'ciao nick1 e nick2',
                'delivery_date': '7/11/2021',
                'submit_button': 'Save as draft',
            }
            file = {'image_file': ''}
            session = requests.session()
            r = requests.post(URL, files=file, cookies=loginCookies, data=payload)
            nick5 = db.session.query(User).filter(User.nickname=="nick5").first()
            nick1 = db.session.query(User).filter(User.nickname=="nick1").first()
            nick2 = db.session.query(User).filter(User.nickname=="nick2").first()
            message_check_nick1=db.session.query(Message).filter(Message.receiver_id==nick1.id).filter(Message.sender_id==nick5.id).filter(Message.body=="ciao nick1 e nick2").filter(Message.is_draft==True).first()
            message_check_nick2=db.session.query(Message).filter(Message.receiver_id==nick2.id).filter(Message.sender_id==nick5.id).filter(Message.body=="ciao nick1 e nick2").filter(Message.is_draft==True).first()
            assert message_check_nick1 is not None and message_check_nick2 is not None

#5) enter in the page without login
    def test_send_email_without_login(self):
        app=create_app()
        with app.app_context():
            URL = 'http://127.0.0.1:5000/send'
            session = requests.session()
            r = requests.get(URL, allow_redirects=False)
            assert r.status_code == 302

#6) message with blacklist
    def test_send_email(self):
        app=create_app()
        with app.app_context():
            URL_login = 'http://127.0.0.1:5000/login'
            payload_login = {
                'email': 'email5',
                'password': 'pass5'
            }
            session_login = requests.session()
            r_login = requests.post(URL_login, data=payload_login)
            loginCookies = r_login.cookies
            URL = 'http://127.0.0.1:5000/send'
            payload = {
                'recipient': 'nick1',
                'body': 'ciao blacklist nick1',
                'delivery_date': '7/11/2021',
                'submit_button': 'Send',
            }
            file = {'image_file': ''}
            nick5 = db.session.query(User).filter(User.nickname=="nick5").first()
            nick1 = db.session.query(User).filter(User.nickname=="nick1").first()
            blacklist_test = BlackList()
            blacklist_test.user_id = nick1.id
            blacklist_test.blacklisted_user_id = nick5.id
            db.session.add(blacklist_test)
            db.session.commit()
            session = requests.session()
            r = requests.post(URL, files=file, cookies=loginCookies, data=payload)
            message_check=db.session.query(Message).filter(Message.receiver_id==nick1.id).filter(Message.sender_id==nick5.id).filter(Message.body=="ciao blacklist nick1").first()
            db.session.delete(blacklist_test)
            db.session.commit()
            test_blacklist_removed = db.session.query(BlackList).filter(BlackList.id==nick1.id).filter(BlackList.blacklisted_user_id==nick5.id).first()
            assert message_check is None and test_blacklist_removed is None
            
#7) message without recipient
    def test_send_email_without_recipient(self):
        app=create_app()
        with app.app_context():
            URL_login = 'http://127.0.0.1:5000/login'
            payload_login = {
                'email': 'email5',
                'password': 'pass5'
            }
            session_login = requests.session()
            r_login = requests.post(URL_login, data=payload_login)
            loginCookies = r_login.cookies
            URL = 'http://127.0.0.1:5000/send'
            payload = {
                'recipient': None,
                'body': 'ciao blacklist nick1',
                'delivery_date': '7/11/2021',
                'submit_button': 'Send',
            }
            file = {'image_file': ''}
            session = requests.session()
            r = requests.get(URL, allow_redirects=False)
            assert r.status_code == 302
            

