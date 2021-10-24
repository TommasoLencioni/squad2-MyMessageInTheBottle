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
            #TODO  finish to populate
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