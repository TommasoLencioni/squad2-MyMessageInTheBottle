#test 
from operator import contains
import requests
from sqlalchemy.sql.expression import true
from monolith.app import *
from monolith.database import BlackList, Message, ReportList

class TestCreate_user:

#1) insert a user into blacklist
    def test_add_blacklist(self):
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
            URL = 'http://127.0.0.1:5000/users'
            session = requests.session()
            nick5 = db.session.query(User).filter(User.nickname=="nick5").first()
            nick1 = db.session.query(User).filter(User.nickname=="nick1").first()
            r = requests.get(URL+'?block_user_id='+str(nick1.id)+'&block=1', cookies=loginCookies) #block user1
            blacklist_check=db.session.query(BlackList).filter(BlackList.user_id==nick5.id).filter(BlackList.blacklisted_user_id==nick1.id).first()
            assert blacklist_check is not None

#2) remove user from blacklist
    def test_remove_blacklist(self):
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
            URL = 'http://127.0.0.1:5000/users'
            session = requests.session()
            nick5 = db.session.query(User).filter(User.nickname=="nick5").first()
            nick1 = db.session.query(User).filter(User.nickname=="nick1").first()
            r = requests.get(URL+'?block_user_id='+str(nick1.id)+'&block=0', cookies=loginCookies) #block user1
            blacklist_check=db.session.query(BlackList).filter(BlackList.user_id==nick5.id).filter(BlackList.blacklisted_user_id==nick1.id).first()
            assert blacklist_check is  None

#3) add two times a user in the balcklist
    def test_double_blacklist(self):
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
            URL = 'http://127.0.0.1:5000/users'
            session = requests.session()
            nick5 = db.session.query(User).filter(User.nickname=="nick5").first()
            nick1 = db.session.query(User).filter(User.nickname=="nick1").first()
            print(URL+'?block_user_id='+str(nick1.id)+'&block=1')
            r_blacklist = requests.get(URL+'?block_user_id='+str(nick1.id)+'&block=1', cookies=loginCookies) #block user1
            blacklist_check=db.session.query(BlackList).filter(BlackList.user_id==nick5.id).filter(BlackList.blacklisted_user_id==nick1.id).first()
            assert blacklist_check is not None


#4) remove two times a user from the blacklist


#5) enter in the page without login
    def test_enter_users_page_without_login(self):
        app=create_app()
        with app.app_context():
            URL = 'http://127.0.0.1:5000/users'
            session = requests.session()
            r = requests.get(URL, allow_redirects=False)
            assert r.status_code == 302

#6) add user in the report list
    def test_add_report_list(self):
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
            URL = 'http://127.0.0.1:5000/users'
            session = requests.session()
            nick5 = db.session.query(User).filter(User.nickname=="nick5").first()
            nick1 = db.session.query(User).filter(User.nickname=="nick1").first()
            r = requests.get(URL+'?block_user_id='+str(nick1.id)+'&block=2', cookies=loginCookies) #block user1
            reportlist_check=db.session.query(ReportList).filter(ReportList.user_id==nick5.id).filter(ReportList.reportlisted_user_id==nick1.id).first()
            assert reportlist_check is not None

#7) add two times a user in the report list