#test
from monolith.auth import *
from monolith.app import *

class TestAuth:

#1) load user test
    def test_load_user_exists(self):
        app=create_app()
        with app.app_context():
            user = load_user(1)
            assert user is not None

#2) load unexist user test
    def test_load_user_not_exists(self):
        app=create_app()
        with app.app_context():
            user = load_user(999)
            assert user is None