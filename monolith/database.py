from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


class User(db.Model):

    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)    # Create unique id for the user
    email = db.Column(db.Unicode(128), nullable=False)                  # Create email for the user
    firstname = db.Column(db.Unicode(128))                              # Firstname of user
    lastname = db.Column(db.Unicode(128))                               # Surname of user
    password = db.Column(db.Unicode(128))                               # Create password for user
    date_of_birth = db.Column(db.Date)                                  # Users date of birth
    location = db.Column(db.Unicode(128))                               # Users location
    nickname = db.Column(db.Unicode(128))                               # Nickname of the user
    is_active = db.Column(db.Boolean, default=False)                    # Checks active status of user (Online/Offline)
    is_admin = db.Column(db.Boolean, default=False)                     # Checks if user is admin or not (True if admin)
    is_deleted = db.Column(db.Boolean, default=False)                   # Checks that the user is deleted or not (True if deleted)
    is_anonymous = False                                                # Checks if user is logged in or not 
    lottery_points = db.Column(db.Integer, default = 0)                 # point winned partecipating to the monthly lottery
    
    def __init__(self, *args, **kw):
        super(User, self).__init__(*args, **kw)
        self._authenticated = False

    # set the user password
    def set_password(self, password):
        self.password = generate_password_hash(password)

    @property
    def is_authenticated(self):
        return self._authenticated

    # return true is the user is authenticated
    def authenticate(self, password):
        checked = check_password_hash(self.password, password)
        self._authenticated = checked
        return self._authenticated

    # Return the user id
    def get_id(self):
        return self.id


class Message(db.Model):
    __tablename__ = 'message'
    #TODO: add a sender/reciever _nickname or name so we can display it
    message_id = db.Column(db.Integer, primary_key=True, autoincrement=True)    # primary key for the message, autoincremental
    sender_id = db.Column(db.Integer, nullable=False)                           # user_id of the sender
    receiver_id = db.Column(db.Integer, nullable=False)                         # user_id of the reciver
    delivery_date = db.Column(db.Date)                                          # scheduled date for sending message
    creation_date = db.Column(db.Date)                                          # Creation date for the message
    body = db.Column(db.Unicode(128), nullable=True)                            # body of the message
    image = db.Column(db.Unicode(1000000), nullable=True)                       # The image unicode (saving image in the db)
    is_delivered = db.Column(db.Boolean, nullable=False, default = False)       # True when a notification is send to the recipient
    is_draft = db.Column(db.Boolean, nullable=True)                             # True when a message is not send, but saved as draft
    opened = db.Column(db.Boolean, nullable=True)                               # True when the message is opened by the recipient
    is_opened_notified = db.Column(db.Boolean, nullable=True, default = False)  # True when the notification is send for an opened message
    deleted = db.Column(db.Boolean, nullable=True)                              # True when a message is delete
    

    def __init__(self, *args, **kw):
        super(Message, self).__init__(*args, **kw)

class Lottery(db.Model):
    __tablename__ = 'lottery'
    contestant_id = db.Column(db.Integer, primary_key=True)                    # user_id of the participant of the lottery

class Filter_list(db.Model):
    __tablename__ = 'filter'
    user_id = db.Column(db.Integer, primary_key=True, nullable=False)
    list = db.Column(db.Unicode(128), nullable=True)

class BlackList(db.Model):
    __tablename__ = 'blacklist'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)           # primary key, autoincremental
    user_id = db.Column(db.Integer, nullable=False)                            # the user_id who hold the Blacklist
    blacklisted_user_id = db.Column(db.Integer, nullable=False)                # the user in the blacklist

class ReportList(db.Model):
    __tablename__ = 'reportlist'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)            # primary key, autoincremental
    user_id = db.Column(db.Integer, nullable=False)                             # the user_id who hold the reportlist
    reportlisted_user_id = db.Column(db.Integer, nullable=False)                # the reported user
    