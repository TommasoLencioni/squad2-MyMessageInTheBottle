import datetime
from flask import Flask
from monolith.auth import login_manager
from monolith.database import User, db, Message
from monolith.views import blueprints
from celery import Celery
import time
from flask_mail import Mail




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

# *************************************************************************** #
### CELERY TASKS ###

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls test('hello') every 10 seconds.
    sender.add_periodic_task(10.0, check.s('hello'), name='check for new message...')

    # Calls test('world') every 30 seconds
#    sender.add_periodic_task(30.0, test.s('world'), expires=10)

    # Executes every Monday morning at 7:30 a.m.
#    sender.add_periodic_task(
#        crontab(hour=7, minute=30, day_of_week=1),
#        test.s('Happy Mondays!'),
#    )

def send_mail(mail):
    pass

@celery.task
def check(arg):
    now = datetime.datetime.now()
    to_notify = db.session.query(Message).filter(Message.is_delivered == False).filter(Message.delivery_date <= now)
    print("/////////////////////////////////////////////////////////////////")
    print(to_notify.all())
    for item in to_notify.all():
        user = db.session.query(User).filter(User.id == item.receiver_id)
        print(user.first().email)
        #send_mail(user.first().email)
    


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
