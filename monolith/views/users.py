from datetime import date, datetime
from re import I
import re
from sqlalchemy import select
import time
import datetime
from flask import Blueprint, redirect, render_template, request
from flask_login import current_user, logout_user

from monolith.database import User, db, Message
from monolith.forms import UserForm, SendForm
from monolith.auth import current_user

from .tasks import create_task

users = Blueprint('users', __name__)


@users.route('/users')
def _users():
    if current_user is not None and hasattr(current_user, 'id'):
        _users = db.session.query(User).filter(User.is_deleted==False)
        return render_template("users.html", users=_users)
    else:
        return redirect('/login')

@users.route('/create_user', methods=['POST', 'GET'])
def create_user():
    form = UserForm()
    if not (current_user is not None and hasattr(current_user, 'id')):
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
    else:
        return "You are currently logged in, you have to <a href=/logout>logout</a> first"  

@users.route('/send', methods=['POST', 'GET'])
def send():
    draftReciever = request.args.get("reciever")
    draftBody = request.args.get("body")
    form = SendForm()
    if draftBody is not None:
        form.body.data=draftBody
    if request.method == 'POST':
        if form.data is not None and form.data['recipient'] is not None:
            for nick in form.data['recipient']:
                new_message = Message()
                form.populate_obj(new_message)
                receiver_id = db.session.query(User).filter(User.nickname == nick)
                new_message.receiver_id = receiver_id.first().id
                
                if request.form['submit_button'] == 'Save as draft':
                    new_message.is_draft = True
                else:
                    new_message.is_draft = False
                    
                if form.data['delivery_date'] is None:
                    new_message.delivery_date=date.today()
                    
                sender= db.session.query(User).filter(User.id == current_user.id)
                new_message.sender_id=sender.first().id
                db.session.add(new_message)
            db.session.commit()
            print('ID e ' + str(new_message.message_id))
            q = db.session.query(User).filter(User.id == current_user.id)
            #TODO blacklist
            user_list = db.session.query(User.nickname).filter(User.id != current_user.id).filter(User.is_admin == False)
            #print(user_list.all())
            new_user_list=[]
            for elem in user_list.all():
                new_user_list.append(str(elem).replace('(','').replace('\'', '').replace(')','').replace(',',''))
            dictUS = {}
            for el in new_user_list:
                    dictUS[el] = 0
            if draftReciever is not None:
                dictUS[draftReciever] = 1
            if new_message.is_draft:
                return render_template("send.html",  current_user=current_user, current_user_firstname=q.first().firstname, form=form, user_list=dictUS, is_draft=True) #TOFIX This redirect to sending_messages
            else:
                return render_template("send.html",  current_user=current_user, current_user_firstname=q.first().firstname, form=form, user_list=dictUS, is_sent=True) #TOFIX This redirect to sending_messages
        
    elif request.method == 'GET':
        if current_user is not None and hasattr(current_user, 'id'):
            #TODO blacklist
            user_list = db.session.query(User.nickname).filter(User.id != current_user.id).filter(User.is_admin == False)
            new_user_list=[]
            for elem in user_list.all():
                new_user_list.append(str(elem).replace('(','').replace('\'', '').replace(')','').replace(',',''))
            dictUS = {}
            for el in new_user_list:
                dictUS[el] = 0
            if draftReciever is not None:
                dictUS[draftReciever] = 1
            q = db.session.query(User).filter(User.id == current_user.id)
            return render_template("send.html", current_user=current_user, current_user_firstname=q.first().firstname, form=form, user_list=dictUS)
        else:
            welcome = None
            return redirect('/login')
  
@users.route('/profile', methods=['GET'])
def profile():
    """
        This functionality allows to users to view the user's profile.
        Retrive the information about the user in the db, and pass as argument
        the values in the 'profile_info.html' template.
        If the user who try to access this service is not logged, will be render in the
        'home' page
    """
    if current_user is not None and hasattr(current_user, 'id'):
        return render_template("profile_info.html", current_user=current_user)
    else:
        return redirect('/login')


@users.route('/deleteAccount', methods=['POST','GET'])
def delete_account():
    """
        This funcionality allows user to delete his/her account from MyMessageInTheBottle.
        The function will delete the account only for the logged user, and will redirect in the start page
    """
    if request.method == 'GET':
        if current_user is not None and hasattr(current_user, 'id'):
            return render_template("delete.html")
        else:
            return redirect('/login')
    else:
        if request.form['confirm_button'] == 'Delete my account':
            if current_user is not None and hasattr(current_user, 'id'):
                query = db.session.query(User).filter(User.id == current_user.id)
                query.first().is_deleted=True
                db.session.commit()
                logout_user()
            return render_template('delete.html', is_deleted=True)
        else:
            return redirect('/')

@users.route('/mailbox', methods=['GET'])
def inbox():
    if current_user is not None and hasattr(current_user, 'id'):
        _sentMessages = db.session.query(Message,User).filter(Message.sender_id == current_user.id).filter(Message.is_draft == False).filter(Message.receiver_id==User.id)
        _recMessages = db.session.query(Message,User).filter(Message.receiver_id == current_user.id).filter(Message.is_draft == False).filter(Message.sender_id==User.id).filter(Message.delivery_date<=datetime.datetime.today())
        _draftMessage = db.session.query(Message,User).filter(Message.sender_id == current_user.id).filter(Message.is_draft == True).filter(Message.receiver_id==User.id)
        return render_template("mailbox.html", messages=_recMessages.all(), sendMessages=_sentMessages.all(), draftMessages=_draftMessage.all())
    else:
        return redirect('/login')

@users.route("/tasks", methods=["POST", "GET"])
def run_task():
    task = create_task.delay(int(5))
    task.wait()
    return({"value":"done"})