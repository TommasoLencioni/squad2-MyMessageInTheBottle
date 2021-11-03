import datetime
from flask import Flask
from monolith.auth import login_manager
from monolith.database import User, db, Message
from monolith.views import blueprints
from celery import Celery
import time
from flask_mail import Mail
from flask_mail import Message as MessageFlask



def make_celery(app):
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
    app = Flask(__name__)
    app.config['CELERY_BROKER_URL'] = 'redis://redis:6379'
    app.config['CELERY_RESULT_BACKEND'] = 'redis://redis:6379'
    app.config['WTF_CSRF_SECRET_KEY'] = 'A SECRET KEY'
    app.config['SECRET_KEY'] = 'ANOTHER ONE'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../mmiab.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAIL_SERVER']='smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USERNAME'] = 'provaase5@gmail.com'
    app.config['MAIL_PASSWORD'] = 'qwertyuiop@123'
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False

    for bp in blueprints:
        app.register_blueprint(bp)
        bp.app = app

    db.init_app(app)
    login_manager.init_app(app)
    db.create_all(app=app)

    # create a first admin user
    with app.app_context():
        q = db.session.query(User).filter(User.email == 'example@example.com')
        user = q.first()
        if user is None:
            example = User()
            example.firstname = 'Admin'
            example.lastname = 'Admin'
            example.email = 'example@example.com'
            example.dateofbirth = datetime.datetime(2020, 10, 5)
            example.is_admin = True
            example.set_password('admin')
            db.session.add(example)
            db.session.commit()

    return app


app = create_app()
celery = make_celery(app)
mail = Mail(app)

# *************************************************************************** #
### CELERY TASKS ###

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls test('hello') every 60 seconds.
    sender.add_periodic_task(60.0, checkNewMessage.s('hello'), name='check for new message...')
    
    # Calls test('hello') every 60 seconds.
    sender.add_periodic_task(60.0, checkMessageOpened.s('hello'), name='check for message opened...')


def send_mail(email, body):
    print ("sending_mail...")
    print("mail destinatario:"+str(email))
    if body is None:
        msg = MessageFlask("You have recived a new message!", sender="provaase5@gmail.com", recipients=[email])
        msg.body = """new message in the "fantastic" social media Message In a Bottle!"""
    elif body is not None:
        msg = MessageFlask("Your message has been read!", sender="provaase5@gmail.com", recipients=[email])
        msg.html = """<p>Your message has been read.</p>
                    <p>Message read:</br>{}</p>""".format(body)
    mail.send(msg)

@celery.task
def checkNewMessage(arg):
    now = datetime.datetime.now()
    to_notify = db.session.query(Message).filter(Message.is_delivered == False).filter(Message.delivery_date <= now)
    print("/////////////////////////////////////////////////////////////////")
    for item in to_notify.all():
        user = db.session.query(User).filter(User.id == item.receiver_id)
        item.is_delivered = True
        db.session.commit()
        print(user.first().email)
        send_mail(user.first().email, None)

@celery.task
def checkMessageOpened(arg):
    to_notify = db.session.query(Message).filter(Message.opened == True).filter(Message.is_opened_notified == False)
    for item in to_notify.all():
        user = db.session.query(User).filter(User.id == item.receiver_id)
        item.is_opened_notified = True
        db.session.commit()
        send_mail(user.first().email, item.body)


@celery.task
def test(arg):
    print(arg)

@celery.task
def add(x, y):
    z = x + y
    print(z)


@celery.task(name="create_task")
def create_task(task_type):
    time.sleep(10)
    print("hello from celery")
    return True













if __name__ == '__main__':
    app.run()
