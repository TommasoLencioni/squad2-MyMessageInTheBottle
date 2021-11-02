from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


class User(db.Model):

    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.Unicode(128), nullable=False)
    firstname = db.Column(db.Unicode(128))
    lastname = db.Column(db.Unicode(128))
    password = db.Column(db.Unicode(128))
    date_of_birth = db.Column(db.DateTime)
    location = db.Column(db.Unicode(128))
    nickname = db.Column(db.Unicode(128))
    propic = db.Column(db.Unicode(128))
    is_active = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_deleted = db.Column(db.Boolean, default=False)
    is_anonymous = False
   # blacklist = db.Column(db.Enum(db.Integer)) #This enum contains the id of the users that this user blacklisted
    #we need to define a class Enum.
    
    def __init__(self, *args, **kw):
        super(User, self).__init__(*args, **kw)
        self._authenticated = False

    def set_password(self, password):
        self.password = generate_password_hash(password)

    @property
    def is_authenticated(self):
        return self._authenticated

    def authenticate(self, password):
        checked = check_password_hash(self.password, password)
        self._authenticated = checked
        return self._authenticated

    def get_id(self):
        return self.id


class Message(db.Model):
    __tablename__ = 'message'
    #TODO: add a sender/reciever _nickname or name so we can display it
    message_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sender_id = db.Column(db.Integer, nullable=False)
    receiver_id = db.Column(db.Integer, nullable=False)
    delivery_date = db.Column(db.DateTime)
    creation_date = db.Column(db.DateTime)
    is_draft = db.Column(db.Boolean, nullable=True)
    body = db.Column(db.Unicode(128), nullable=True)
    is_opening = db.Column(db.Boolean, nullable=True)
    opened = db.Column(db.Boolean, nullable=True)

    def __init__(self, *args, **kw):
        super(Message, self).__init__(*args, **kw)
 
