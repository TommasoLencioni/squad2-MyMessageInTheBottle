from flask import Blueprint, redirect, render_template, request

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
            print(new_message.receiver_id)
            print('Text should be here' + new_message.body)
            print(new_message.message_id)
            print(new_message.is_draft)
            print(new_message.delivery_date)
            sender= db.session.query(User).filter(User.id == current_user.id)
            new_message.sender_id=sender.first().id
            print(new_message.sender_id)
            return redirect('/users')
    elif request.method == 'GET':
        if current_user is not None and hasattr(current_user, 'id'):
            q = db.session.query(User).filter(User.id == current_user.id)
            #print(q.firstname)
            print(q.first().firstname)
            return render_template("send.html", current_user=q.first().firstname, form=form)
        else:
            welcome = None
            return render_template("index.html", welcome=welcome)
    
    