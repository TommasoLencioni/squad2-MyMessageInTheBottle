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
    lottery_points = db.Column(db.Integer, default = 0)
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
    
    creation_date = db.Column(db.DateTime)                                  # create_date for the message
    body = db.Column(db.Unicode(128), nullable=True)                        # body of the message
    is_delivered = db.Column(db.Boolean, nullable=False, default = False)   # True when a notification is send to the recipient for advise him that ricived new message
    is_draft = db.Column(db.Boolean, nullable=True)                         # when a message is not send, but saved as draft
    opened = db.Column(db.Boolean, nullable=True)                           # True when the message is opened by the recipient
    is_opened_notified = db.Column(db.Boolean, nullable=True, default = False)               # True when the notification is send for an opened message
    deleted = db.Column(db.Boolean, nullable=True)                          # True when a message is delete
    image = db.Column(db.Unicode(1000000), nullable=True)

    def __init__(self, *args, **kw):
        super(Message, self).__init__(*args, **kw)

class Lottery(db.Model):
    __tablename__ = 'lottery'
    contestant_id = db.Column(db.Integer, primary_key=True)

class Filter_list(db.Model):
    __tablename__ = 'filter'
    user_id = db.Column(db.Integer, primary_key=True, nullable=False)
    list = db.Column(db.Unicode(128), nullable=True)

class BlackList(db.Model):
    __tablename__ = 'blacklist'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)
    blacklisted_user_id = db.Column(db.Integer, nullable=False)

class ReportList(db.Model):
    __tablename__ = 'reportlist'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)
    reportlisted_user_id = db.Column(db.Integer, nullable=False)
    