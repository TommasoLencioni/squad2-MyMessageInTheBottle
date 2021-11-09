#test
import unittest
from monolith.auth import *
from monolith.app import *
from monolith.app import app as TestedApp
import unittest
import json

class TestAuth(unittest.TestCase):

#1) load user test
    def test_load_user_exists(self):
        with app.app_context():
            app2=TestedApp.test_client()
            user = load_user(1)
            assert user is not None

#2) load unexist user test
    def test_load_user_not_exists(self):
        with app.app_context():
            app2=TestedApp.test_client()
            user = load_user(999)
            assert user is None
