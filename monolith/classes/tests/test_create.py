from re import U
import unittest
import requests
from sqlalchemy.sql.expression import true
from monolith.app import *
from monolith.app import app as TestedApp
import unittest
import json
from monolith.database import BlackList, Filter_list, Message, ReportList

LOGIN_OK = 200
LOGIN_FAIL = 201
DOUBLE_LOGIN = 202

class Test(unittest.TestCase):
#test create

#1) new user
    def test_create_user(self):
        with app.app_context():
            app2=TestedApp.test_client()
            URL = '/create_user'
            payload = {
                'email': 'email5',
                'firstname': 'name5',
                'lastname': 'last5',
                'password': 'pass5',
                'date_of_birth': '1/01/2000',
                'nickname': 'nick5',
                'location': 'Pisa'
            }
            app2.post(URL, data=payload)
            user_check=db.session.query(User).filter(User.email=='email5').first()
            assert user_check is not None

#2) new user with same email 
    def test_create_user_same_email(self):
        with app.app_context():
            app2=TestedApp.test_client()
            URL = '/create_user'
            payload = {
                'email': 'email5',
                'firstname': 'name',
                'lastname': 'last',
                'password': 'pass',
                'date_of_birth': '1/01/2000',
                'nickname': 'nick',
                'location': 'Pisa'
            }
            r = app2.post(URL, data=payload)
            assert r.status_code == 302


#3) new user with same nickname
    def test_create_user_same_nick(self):
        with app.app_context():
            app2=TestedApp.test_client()
            URL = '/create_user'
            payload = {
                'email': 'email',
                'firstname': 'name',
                'lastname': 'last',
                'password': 'pass',
                'date_of_birth': '1/01/2000',
                'nickname': 'nick5',
                'location': 'Pisa'
            }
            r = app2.post(URL, data=payload)
            #assert r.url == 'http://127.0.0.1:5000/create_user'
            assert r.status_code == 302

#test login

#1) login
    def test_login_user(self):
        with app.app_context():
            app2=TestedApp.test_client()
            URL = '/login'
            payload = {
                'email': 'email5',
                'password': 'pass5'
            }
            r = app2.post(URL, data=payload)
            assert r.status_code == LOGIN_OK

#2) wrong login
    def test_wrong_login_user(self):
        with app.app_context():
            app2=TestedApp.test_client()
            URL = '/login'
            payload = {
                'email': 'email5',
                'password': 'pass1000'
            }
            r = app2.post(URL, data=payload)
            assert r.status_code == LOGIN_FAIL

#3) login when just login
    def test_login_user_when_just_login(self):
        with app.app_context():
            app2=TestedApp.test_client()
            URL = '/login'
            payload = {
                'email': 'email5',
                'password': 'pass5'
            }
            r1 = app2.post(URL, data=payload)
            r = app2.post(URL, data=payload)
            assert r.status_code == DOUBLE_LOGIN

#test user

    #1) insert a user into blacklist
    def test_z_add_blacklist(self):
        with app.app_context():
            app2=TestedApp.test_client()
            URL_login = '/login'
            payload = {
                'email': 'email5',
                'password': 'pass5'
            }
            r1 = app2.post(URL_login, data=payload)
            URL = '/users'
            nick5 = db.session.query(User).filter(User.nickname=="nick5").first()
            nick1 = db.session.query(User).filter(User.nickname=="nick1").first()
            r = app2.get(URL+'?block_user_id='+str(nick1.id)+'&block=1') #block user1
            blacklist_check=db.session.query(BlackList).filter(BlackList.user_id==nick5.id).filter(BlackList.blacklisted_user_id==nick1.id).first()
            assert blacklist_check is not None

#2) remove user from blacklist
    def test_z_remove_blacklist(self):
        with app.app_context():
            app2=TestedApp.test_client()
            URL_login = '/login'
            payload = {
                'email': 'email5',
                'password': 'pass5'
            }
            r1 = app2.post(URL_login, data=payload)
            URL = '/users'
            nick5 = db.session.query(User).filter(User.nickname=="nick5").first()
            nick1 = db.session.query(User).filter(User.nickname=="nick1").first()
            r = app2.get(URL+'?block_user_id='+str(nick1.id)+'&block=0') #free user1
            blacklist_check=db.session.query(BlackList).filter(BlackList.user_id==nick5.id).filter(BlackList.blacklisted_user_id==nick1.id).first()
            assert blacklist_check is  None

#3) add two times a user in the balcklist
    def test_z_double_blacklist(self):
        with app.app_context():
            app2=TestedApp.test_client()
            URL_login = '/login'
            payload_login = {
                'email': 'email5',
                'password': 'pass5'
            }
            r_login = app2.post(URL_login, data=payload_login)
            URL = '/users'
            nick5 = db.session.query(User).filter(User.nickname=="nick5").first()
            nick1 = db.session.query(User).filter(User.nickname=="nick1").first()
            r_blacklist = app2.get(URL+'?block_user_id='+str(nick1.id)+'&block=1') #block user1
            r = app2.get(URL+'?block_user_id='+str(nick1.id)+'&block=1') #block user1
            blacklist_check=db.session.query(BlackList).filter(BlackList.user_id==nick5.id).filter(BlackList.blacklisted_user_id==nick1.id).count()
            assert blacklist_check == 1


#4) remove two times a user from the blacklist
    def test_z_double_remove_blacklist(self):
        with app.app_context():
            app2=TestedApp.test_client()
            URL_login = '/login'
            payload_login = {
                'email': 'email5',
                'password': 'pass5'
            }
            r_login = app2.post(URL_login, data=payload_login)
            URL = '/users'
            nick5 = db.session.query(User).filter(User.nickname=="nick5").first()
            nick1 = db.session.query(User).filter(User.nickname=="nick1").first()
            r_blacklist = app2.get(URL+'?block_user_id='+str(nick1.id)+'&block=0') #free user1
            r = app2.get(URL+'?block_user_id='+str(nick1.id)+'&block=0') #free user1
            blacklist_check=db.session.query(BlackList).filter(BlackList.user_id==nick5.id).filter(BlackList.blacklisted_user_id==nick1.id).first()
            assert blacklist_check is None

#5) enter in the page without login
    def test_enter_users_page_without_login(self):
        with app.app_context():
            app2=TestedApp.test_client()
            URL = '/users'
            r = app2.get(URL)
            assert r.status_code == 302

#6) add user in the report list
    def test_add_report_list(self):
        with app.app_context():
            app2=TestedApp.test_client()
            URL_login = '/login'
            payload_login = {
                'email': 'email5',
                'password': 'pass5'
            }
            r_login = app2.post(URL_login, data=payload_login)
            URL = '/users'
            nick5 = db.session.query(User).filter(User.nickname=="nick5").first()
            nick1 = db.session.query(User).filter(User.nickname=="nick1").first()
            r = app2.get(URL+'?block_user_id='+str(nick1.id)+'&block=2') #report user1
            reportlist_check=db.session.query(ReportList).filter(ReportList.user_id==nick5.id).filter(ReportList.reportlisted_user_id==nick1.id).first()
            assert reportlist_check is not None

#7) add two times a user in the report list
    def test_double_add_report_list(self):
        with app.app_context():
            app2=TestedApp.test_client()
            URL_login = '/login'
            payload_login = {
                'email': 'email5',
                'password': 'pass5'
            }
            r_login = app2.post(URL_login, data=payload_login)
            URL = '/users'
            nick5 = db.session.query(User).filter(User.nickname=="nick5").first()
            nick1 = db.session.query(User).filter(User.nickname=="nick1").first()
            r_report = app2.get(URL+'?block_user_id='+str(nick1.id)+'&block=2') #report user1
            r = app2.get(URL+'?block_user_id='+str(nick1.id)+'&block=2') #report user1
            reportlist_check=db.session.query(ReportList).filter(ReportList.user_id==nick5.id).filter(ReportList.reportlisted_user_id==nick1.id).count()
            assert reportlist_check == 1

#test send

    #1) send email
    def test_send_email(self):
        with app.app_context():
            app2=TestedApp.test_client()
            URL_login = '/login'
            payload_login = {
                'email': 'email5',
                'password': 'pass5'
            }
            r_login = app2.post(URL_login, data=payload_login)
            URL = '/send'
            payload = {
                'recipient': 'nick1',
                'body': 'ciao nick1',
                'delivery_date': '7/11/2021',
                'submit_button': 'Send',
            }
            file = {'image_file': ''}
            r = app2.post(URL, data=payload)
            nick5 = db.session.query(User).filter(User.nickname=="nick5").first()
            nick1 = db.session.query(User).filter(User.nickname=="nick1").first()
            message_check=db.session.query(Message).filter(Message.receiver_id==nick1.id).filter(Message.sender_id==nick5.id).filter(Message.body=="ciao nick1").first()
            assert message_check is not None

#2) send email to multiple user
    def test_send_email_multiple_users(self):
        with app.app_context():
            app2=TestedApp.test_client()
            URL_login = '/login'
            payload_login = {
                'email': 'email5',
                'password': 'pass5'
            }
            r_login = app2.post(URL_login, data=payload_login)
            URL = '/send'
            payload = {
                'recipient': ['nick1','nick2'],
                'body' : 'ciao nick1 e nick2',
                'delivery_date': '7/11/2021',
                'submit_button': 'Send',
            }
            file = {'image_file': ''}
            r = app2.post(URL, data=payload)
            nick5 = db.session.query(User).filter(User.nickname=="nick5").first()
            nick1 = db.session.query(User).filter(User.nickname=="nick1").first()
            nick2 = db.session.query(User).filter(User.nickname=="nick2").first()
            print(nick1.id)
            print(nick2.id)
            message_check_nick1=db.session.query(Message).filter(Message.receiver_id==nick1.id).filter(Message.sender_id==nick5.id).filter(Message.body=="ciao nick1 e nick2").first()
            message_check_nick2=db.session.query(Message).filter(Message.receiver_id==nick2.id).filter(Message.sender_id==nick5.id).filter(Message.body=="ciao nick1 e nick2").first()
            assert message_check_nick1 is not None and message_check_nick2 is not None

#3) draft email
    def test_draft_email(self):
        with app.app_context():
            app2=TestedApp.test_client()
            URL_login = '/login'
            payload_login = {
                'email': 'email5',
                'password': 'pass5'
            }
            r_login = app2.post(URL_login, data=payload_login)
            URL = '/send'
            payload = {
                'recipient': 'nick1',
                'body': 'ciao draft nick1',
                'delivery_date': '7/11/2021',
                'submit_button': 'Save as draft',
            }
            file = {'image_file': ''}
            r = app2.post(URL, data=payload)
            nick5 = db.session.query(User).filter(User.nickname=="nick5").first()
            nick1 = db.session.query(User).filter(User.nickname=="nick1").first()
            print(nick1.id)
            message_check=db.session.query(Message).filter(Message.receiver_id==nick1.id).filter(Message.sender_id==nick5.id).filter(Message.body=="ciao draft nick1").filter(Message.is_draft==True).first()
            assert message_check is not None

#4) draft email to multiple users
    def test_draft_email_multiple_users(self):
        with app.app_context():
            app2=TestedApp.test_client()
            URL_login = '/login'
            payload_login = {
                'email': 'email5',
                'password': 'pass5'
            }
            r_login = app2.post(URL_login, data=payload_login)
            URL = '/send'
            payload = {
                'recipient': ['nick1','nick2'],
                'body' : 'ciao nick1 e nick2',
                'delivery_date': '7/11/2021',
                'submit_button': 'Save as draft',
            }
            file = {'image_file': ''}
            r = app2.post(URL, data=payload)
            nick5 = db.session.query(User).filter(User.nickname=="nick5").first()
            nick1 = db.session.query(User).filter(User.nickname=="nick1").first()
            nick2 = db.session.query(User).filter(User.nickname=="nick2").first()
            print(nick1.id)
            print(nick2.id)
            message_check_nick1=db.session.query(Message).filter(Message.receiver_id==nick1.id).filter(Message.sender_id==nick5.id).filter(Message.body=="ciao nick1 e nick2").filter(Message.is_draft==True).first()
            message_check_nick2=db.session.query(Message).filter(Message.receiver_id==nick2.id).filter(Message.sender_id==nick5.id).filter(Message.body=="ciao nick1 e nick2").filter(Message.is_draft==True).first()
            assert message_check_nick1 is not None and message_check_nick2 is not None

#5) enter in the page without login
    def test_send_email_without_login(self):
        with app.app_context():
            app2=TestedApp.test_client()
            URL = '/send'
            r = app2.get(URL)
            assert r.status_code == 302

#6) message with blacklist
    def test_send_email(self):
        with app.app_context():
            app2=TestedApp.test_client()
            URL_login = '/login'
            payload_login = {
                'email': 'email5',
                'password': 'pass5'
            }
            r_login = app2.post(URL_login, data=payload_login)
            URL = '/send'
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
            r = app2.post(URL, data=payload)
            message_check=db.session.query(Message).filter(Message.receiver_id==nick1.id).filter(Message.sender_id==nick5.id).filter(Message.body=="ciao blacklist nick1").first()
            db.session.delete(blacklist_test)
            db.session.commit()
            test_blacklist_removed = db.session.query(BlackList).filter(BlackList.id==nick1.id).filter(BlackList.blacklisted_user_id==nick5.id).first()
            assert message_check is None and test_blacklist_removed is None
            

#test profile

#1) change info
    def test_change_info(self):
        with app.app_context():
            app2=TestedApp.test_client()
            URL_login = '/login'
            payload_login = {
                'email': 'email5',
                'password': 'pass5'
            }
            r_login = app2.post(URL_login, data=payload_login)
            URL = '/profile'
            payload = {
                'firstname': 'name_test',
                'surname': 'surname_test',
                'new_password': 'pass_test',
                'old_password': 'pass5',
                'submit_button': 'Save changes',
            }
            nick5 = db.session.query(User).filter(User.nickname=="nick5").first()
            r = app2.post(URL, data=payload)
            db_check=db.session.query(User).filter(User.id==nick5.id).filter(User.firstname=="name_test").filter(User.lastname=="surname_test").first()
            assert db_check is not None

#2) change info with wrong password
    def test_change_info_wrong_password(self):
        with app.app_context():
            app2=TestedApp.test_client()
            URL_login = '/login'
            payload_login = {
                'email': 'email5',
                'password': 'pass5'
            }
            r_login = app2.post(URL_login, data=payload_login)
            URL = '/profile'
            payload = {
                'firstname': 'name_test',
                'surname': 'surname_test',
                'new_password': 'pass_test',
                'old_password': 'wrong_pass',
                'submit_button': 'Save changes',
            }
            nick5 = db.session.query(User).filter(User.nickname=="nick5").first()
            r = app2.post(URL, data=payload)
            db_check=db.session.query(User).filter(User.id==nick5.id).filter(User.firstname=="name_test").filter(User.lastname=="surname_test").first()
            assert db_check is None
            
#3) word filter
    def test_change_filter(self):
        with app.app_context():
            app2=TestedApp.test_client()
            URL_login = '/login'
            payload_login = {
                'email': 'email5',
                'password': 'pass5'
            }
            r_login = app2.post(URL_login, data=payload_login)
            URL = '/profile'
            payload = {
                'filter': 'ciao,addio',
                'submit_button': 'Submit',
            }
            nick5 = db.session.query(User).filter(User.nickname=="nick5").first()
            r = app2.post(URL, data=payload)
            db_check=db.session.query(Filter_list).filter(Filter_list.user_id==nick5.id).filter(Filter_list.list=="ciao,addio").first()
            assert db_check is not None

#4) profile without login
    def test_enter_profile_page_without_login(self):
        with app.app_context():
            app2=TestedApp.test_client()
            URL = '/profile'
            r = app2.get(URL)
            assert r.status_code == 302


#test logout

#1) logout
    def test_logout(self):
        with app.app_context():
            app2=TestedApp.test_client()
            URL_login = '/login'
            payload_login = {
                'email': 'email5',
                'password': 'pass5'
            }
            r_login = app2.post(URL_login, data=payload_login)
            URL = '/logout'
            nick5 = db.session.query(User).filter(User.nickname=="nick5").first()
            r = app2.get(URL)
            print(db.session.query(User).filter(User.nickname=="nick5").first().is_active)
            db_check=db.session.query(User).filter(User.id==nick5.id).filter(User.is_active==False).first()
            assert db_check is not None

#2) logout_without login
    def test_logout_without_login(self):
        with app.app_context():
            app2=TestedApp.test_client()
            URL = '/logout'
            nick5 = db.session.query(User).filter(User.nickname=="nick5").first()
            r = app2.get(URL)
            assert r.status_code == 302

#test delete account

#1) delete account get
    def test_delete_account_get(self):
        with app.app_context():
            app2=TestedApp.test_client()
            URL_login = '/login'
            payload_login = {
                'email': 'email5',
                'password': 'pass5'
            }
            r_login = app2.post(URL_login, data=payload_login)
            URL = '/deleteAccount'
            r = app2.get(URL)
            assert r.status_code == 200
 

#2) delete account get without login
    def test_delete_account_get_without_login(self):
        with app.app_context():
            app2=TestedApp.test_client()
            URL = '/deleteAccount'
            nick5 = db.session.query(User).filter(User.nickname=="nick5").first()
            r = app2.get(URL)
            assert r.status_code == 302

