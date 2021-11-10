import datetime
from flask import Flask
from monolith.auth import login_manager
from monolith.database import User, db, Message, Lottery
from monolith.views import blueprints
from celery import Celery
from flask_mail import Mail
from flask_mail import Message as MessageFlask
from celery.schedules import crontab
from random import randint


def make_celery(app):
    '''
        Function for create Celery instance 
    '''
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


def create_app():
    '''
        Create an app instance
    '''
    app = Flask(__name__)
    app.config['CELERY_BROKER_URL'] = 'redis://redis:6379'
    app.config['CELERY_RESULT_BACKEND'] = 'redis://redis:6379'
    app.config['WTF_CSRF_SECRET_KEY'] = 'A SECRET KEY'
    app.config['SECRET_KEY'] = 'ANOTHER ONE'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../mmiab.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAIL_SERVER']='smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USERNAME'] = 'asemmib5@gmail.com'
    app.config['MAIL_PASSWORD'] = 'qwertyuiop@1234'
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False

    for bp in blueprints:
        app.register_blueprint(bp)
        bp.app = app

    db.init_app(app)
    login_manager.init_app(app)
    db.create_all(app=app)

    # create a first admin user with default parameter
    with app.app_context():
        q = db.session.query(User).filter(User.email == 'admin@example.com')
        d = db.session.query(User).filter(User.email != 'admin@example.com').count()
        user = q.first()
        if user is None and d==0:
            example = User()
            example.firstname = 'Admin'
            example.lastname = 'Admin'
            example.email = 'admin@example.com'
            example.dateofbirth = datetime.datetime(2020, 10, 5)
            example.is_admin = True
            example.set_password('admin')
            db.session.add(example)
            db.session.commit()
    return app

#create app, celery and mail 
app = create_app()
celery = make_celery(app)
mail = Mail(app)
# *************************************************************************** #
# *************************************************************************** #

                            ### CELERY TASKS ###


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    '''
        Set the time for Celery tasks:
         - every 1 minute execute the task "checkNewMessage"
         - every 1 minute execute the task "checkMessageOpened"
         - every month at day 1 and time 11:00 execute the task "lottery"
    '''
    # NOTIFY FOR A MESSAGE RECEIVED: Executes every minute
    sender.add_periodic_task(60.0, checkNewMessage.s(), name='check for new message received...')
    
    # NOTIFY FOR A MESSAGE OPENED: Executes every minute
    sender.add_periodic_task(60.0, checkMessageOpened.s(), name='check for message opened...')

    # LOTTERY: Executes every month
    sender.add_periodic_task(
        crontab(hour=11, minute=00, day_of_month='1'), lottery.s())

def send_mail(email, body):
    '''
        This function will send mail at users provided in "email" field.
        In case the body is none the function will be called from "checkNewMessage" task,
        otherwise will be called from "checkMessageOpened" task.
    '''

    print ("sending_mail...")

    # Case "new message received"
    if body is None:
        msg = MessageFlask("You have recived a new message!", sender="provaase5@gmail.com", recipients=[email])
        msg.body = """new message in the "fantastic" social media Message In a Bottle!"""
    
    # Case "message opened"
    elif body is not None:
        msg = MessageFlask("Your message has been read!", sender="provaase5@gmail.com", recipients=[email])
        msg.html = """<p>Your message has been read.</p>
                    <p>Message read:</br>{}</p>""".format(body)

    if mail.send(msg):
        return False
    else:
        return True


def send_mail_lottery(email, winner):
    '''
        Will send an email after the lottery task to all users, for announcing the winner
    '''
    print("sending lottery mail...")
    msg = MessageFlask("Monthly winner!", sender="provaase5@gmail.com", recipients=email)
    msg.html = """<p>The monthly winner for the lottery is....</p>
                    <h2>{}</h2>""".format(winner)
    mail.send(msg)

@celery.task
def checkNewMessage():
    '''
        This method will notify the user when recive a new message.
        This method also send the message to users.
    '''

    # Take current time
    now = datetime.datetime.now()

    # Retrive all the message delivered and not notified
    to_notify = db.session.query(Message).filter(Message.is_delivered == False).filter(Message.delivery_date <= now)

    # For-each message, flag it as notified and send an email to the user
    for item in to_notify.all():
        user = db.session.query(User).filter(User.id == item.receiver_id)
        item.is_delivered = True
        db.session.commit()
        send_mail(user.first().email, None)


@celery.task
def checkMessageOpened():
    '''
        This method will send a notification when a send message has been opened
    '''
    
    # Retrive all the message opened and not notified
    to_notify = db.session.query(Message).filter(Message.opened == True).filter(Message.is_opened_notified == False)

    # For-each message, flag it as notified and send an email to the user
    for item in to_notify.all():
        user = db.session.query(User).filter(User.id == item.sender_id)
        item.is_opened_notified = True
        db.session.commit()
        print(user.first().email)
        send_mail(user.first().email, item.body)

    return True


@celery.task
def lottery():
    '''
        Recover all the participants to the lottery and extract a random winner.
        Will add "1 lottery point" to the winner
        At the end send an email to all participant with the nickname of the winner.
    '''
    print("lottery task")
    # List of participants
    list_participant = []
    
    # Retrive the participants to the montlhy lottery
    participants = db.session.query(Lottery)
    if participants.all():
        print("partecipanti: "+str(participants.all()))
        for user in participants.all(): 
            print(user)
            print(user.contestant_id)
            list_participant.append(user.contestant_id)
        
        #Reset monthly lottery table
        addresses = db.session.query(Lottery)
        addresses.delete()
        db.session.commit()

        if len(list_participant) == 0:
            return False

        # Extract a random winner
        winner = randint(0,len(list_participant)-1)
        print("winner: " + str(winner))

        winner = list_participant[winner]
        
        # Increment user points
        user_winner = db.session.query(User).filter(User.id == winner)
        user_winner.first().lottery_points += 1
        db.session.commit()

        # Send mail to all participants to show the winner
        nickname_winner = user_winner.first().nickname

        email_user_list = []
        for item in list_participant:
            participant = db.session.query(User).filter(User.id == item)
            email_user_list.append(participant.first().email)
        send_mail_lottery(email_user_list,nickname_winner)

        return True

if __name__ == '__main__':
    app.run()
