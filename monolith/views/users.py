from datetime import date, datetime
from re import I
from sqlalchemy import select
import time
import datetime
from flask import Blueprint, redirect, render_template, request
from flask_login import current_user

from monolith.database import User, db, Message
from monolith.forms import UserForm, SendForm
from monolith.auth import current_user

users = Blueprint('users', __name__)


@users.route('/users')
def _users():
    _users = db.session.query(User)
    return render_template("users.html", users=_users)


@users.route('/create_user', methods=['POST', 'GET'])
def create_user():
    form = UserForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            new_user = User()
            form.populate_obj(new_user)
            """
            Password should be hashed with some salt. For example if you choose a hash function x, 
            where x is in [md5, sha1, bcrypt], the hashed_password should be = x(password + s) where
            s is a secret key.
            """
            new_user.set_password(form.password.data)
            db.session.add(new_user)
            db.session.commit()
            return redirect('/users')
        else:
            return render_template('create_user.html', form=form, fail_date=True)
    elif request.method == 'GET':
        return render_template('create_user.html', form=form)
    else:
        raise RuntimeError('This should not happen!')

@users.route('/send', methods=['POST', 'GET'])
def send():
    form = SendForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            new_message = Message()
            form.populate_obj(new_message)

            #the value of the recipient_id
            receiver_id = db.session.query(User).filter(User.email == request.form["recipient"])
            new_message.receiver_id = receiver_id.first().id
            print(new_message.receiver_id)

            #new_message.body = request.form['body']
            print('Text should be here: ' + new_message.body)

            print(new_message.message_id)

            #is_draft values 
            if request.form['submit_button'] == 'Save as draft':
                new_message.is_draft = True
            else:
                new_message.is_draft = False
            print(new_message.is_draft)

            #new_message.delivery_date = request.form['delivery_date']
            print(new_message.delivery_date)

            sender= db.session.query(User).filter(User.id == current_user.id)
            new_message.sender_id=sender.first().id
            print(new_message.sender_id)

            #creation date values
            new_message.creation_date = datetime.date.today()
            print(new_message.creation_date)

            print(db.session.execute(select(Message)))

            #db adding
            db.session.add(new_message)
            db.session.commit()
            
            return redirect('/users') #TOFIX This redirect is a stub
    elif request.method == 'GET':
        if current_user is not None and hasattr(current_user, 'id'):
            q = db.session.query(User).filter(User.id == current_user.id)
            #print(q.firstname)
            print(q.first().firstname)
            return render_template("send.html", current_user=q.first().firstname, form=form)
        else:
            welcome = None
            return render_template("index.html", welcome=welcome)


@users.route('/profile', methods=['GET'])
def profile():
    """
        This functionality allows to users to view the user's profile.
        Retrive the information about the user in the db, and pass as argument
        the values in the 'profile_info.html' template.
        If the user who try to access this service is not logged, will be render in the
        'home' page
    """
    return render_template("profile_info.html", current_user=current_user)


@users.route('/deleteAccount', methods=['POST','GET'])
def delete_account():
    """
        This funcionality allows user to delete his/her account from MyMessageInTheBottle.
        The function will delete the account only for the logged user, and will redirect in the start page
    """
    if current_user is not None and hasattr(current_user, 'id'):
        query = db.session.query(User).filter(User.id == current_user.id).delete()
        db.session.commit()
    return render_template("delete.html")

@users.route('/mailbox', methods=['GET'])
def inbox():
    _recMessages = db.session.query(Message).filter(Message.receiver_id == current_user.id)
    _sentMessages = db.session.query(Message).filter(Message.sender_id == current_user.id)
    return render_template("mailbox.html", messages=_recMessages, sendMessages=_sentMessages)