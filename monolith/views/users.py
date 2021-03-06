from datetime import date, datetime
import os
from re import I, U
import re
from types import MethodDescriptorType
from flask.helpers import flash
from sqlalchemy import select
import datetime
from flask import Flask, Blueprint, blueprints, redirect, render_template, request, flash
from flask_login import current_user, logout_user
from sqlalchemy.orm import query
from werkzeug.security import check_password_hash, generate_password_hash
import base64
from monolith.database import BlackList, ReportList, User, db, Message, Filter_list,Lottery
from monolith.forms import UserForm, SendForm
from monolith.auth import current_user
from random import randint

# Point necessary for withdraw a scheduled/sended message
POINT_NECESSARY = 12

users = Blueprint('users', __name__)

#This is the route to see all the user that are registered adn to see who is online
@users.route('/users')
def _users():
    '''
        Show a list of the online and offline users registered to MessageInABottle.
        Also provide the functionality for block and report a user.
    '''
    if current_user is not None and hasattr(current_user, 'id'): #check if the user is logged
        new_blackList = BlackList()
        new_reportlist = ReportList()
        new_blackList.user_id = current_user.id
        new_blackList.blacklisted_user_id = request.args.get("block_user_id") #is the id of the user that he wants to block (it could be put in the URL)

        if new_blackList.blacklisted_user_id is not None: #chek if in the URL there is the id of the user to block
            
            # put user in the blacklist
            if request.args.get("block") == "1": #is a parameter thar could be in the URL to identify the blacklist action
                
                _list = db.session.query(BlackList).filter(BlackList.user_id==new_blackList.user_id).filter(BlackList.blacklisted_user_id==new_blackList.blacklisted_user_id)
                if _list.first() is not None: #chek if the tupla (current_user.id,user_to_block.id) is just in the db
                    print("blacklist already exist")
                else:
                    db.session.add(new_blackList)
                    db.session.commit()
                    print("blacklist add")

            #remove user from the blacklist
            elif request.args.get("block") == "0": 
                blacklist_id = db.session.query(BlackList).filter(BlackList.user_id==new_blackList.user_id).filter(BlackList.blacklisted_user_id==new_blackList.blacklisted_user_id)
                if blacklist_id.first() is not None: #chek if the tupla (current_user.id,user_to_block.id) is just in the db
                    db.session.query(BlackList).filter(BlackList.id==blacklist_id.first().id).delete()
                    db.session.commit()
                    print("removed from blacklist")
                else:
                    print("operation not allowed: the user is not in the blacklist")
            #put a user in the reportlist
            else: 
                new_reportlist.user_id = current_user.id
                new_reportlist.reportlisted_user_id = request.args.get("block_user_id")
                _list = db.session.query(ReportList).filter(ReportList.user_id==new_reportlist.user_id).filter(ReportList.reportlisted_user_id==new_reportlist.reportlisted_user_id)
                if _list.first() is not None:  #chek if the tupla (current_user.id,user_to_report.id) is just in the db
                    print("user already reported")
                else:
                    db.session.add(new_reportlist)
                    db.session.commit()
                    print("added to reportlist")
        _users = db.session.query(User).filter(User.is_deleted==False).filter(User.id!=current_user.id)
        return render_template("users.html", users=_users)
    else:
        return redirect('/login')

#This is the route to create a new user
@users.route('/create_user', methods=['POST', 'GET'])
def create_user():
    '''
        Create a user
    '''
    form = UserForm()
    if not (current_user is not None and hasattr(current_user, 'id')): #check if the user is logged
        if request.method == 'POST': #take information from the Form
            email_exist_control = db.session.query(User).filter(User.email==form.email.data)
            if email_exist_control.first() is not None: #check if the email exists 
                flash("This email is already registered, please try another!")
                return redirect("/create_user")
            nick_exist_control = db.session.query(User).filter(User.nickname==form.nickname.data)
            if nick_exist_control.first() is not None: #check if the nickname exists
                flash("This nickname is not available, please try another!")
                return redirect("/create_user")
            new_user = User()
            form.populate_obj(new_user)
            new_user.set_password(form.password.data)
            db.session.add(new_user)
            db.session.commit()
            return redirect('/users')
        elif request.method == 'GET': #show the form
            return render_template('create_user.html', form=form)
        else:
            raise RuntimeError('This should not happen!')
    else:
        return "You are currently logged in, you have to <a href=/logout>logout</a> first"  

#This is the route to send messages, create drafts, modify draft messages or send them 
@users.route('/send', methods=['POST', 'GET'])
def send():
    isDraft =False                                                  # The message by default is set as "NOT A DRAFT"
    draftReciever = request.args.get("reciever")                    # take argument "reciever"
    draftBody = request.args.get("body")                            # take argument "body"
    isReply = request.args.get("reply")                             # take arument reply
    draft_id = request.args.get('draft_id')                         # # take argument "draft_id"
    form = SendForm()
    if request.method == 'POST':
        if form.data is not None and form.data['recipient'] is not None: #check if the receiver is None
            # check for images
            if request.files['image_file'] is not None:
                image_binary=base64.b64encode(request.files['image_file'].read())
            else:
                image_binary = ""
            #check if the send or draft buttom is pressed
            if request.form['submit_button'] == "Send" or request.form['submit_button'] == 'Save as draft':
                if draft_id is not None:
                    draft_message=db.session.query(Message).filter(Message.message_id==draft_id).delete()
                for nick in form.data['recipient']: #for each receiver that specified in the form create a message
                    new_message = Message()
                    form.populate_obj(new_message)
                    receiver_id = db.session.query(User).filter(User.nickname == nick)
                    new_message.receiver_id = receiver_id.first().id   
                    if request.form['submit_button'] == 'Save as draft': #check whitch button is pressed and set the corresponding flag
                        new_message.is_draft = True
                    else:
                        new_message.is_draft = False
                    if form.data['delivery_date'] is None: #if no date is specified, the current date is put
                        new_message.delivery_date=date.today()
                    new_message.creation_date=date.today()
                    sender= db.session.query(User).filter(User.id == current_user.id)
                    new_message.sender_id=sender.first().id
                    new_message.opened = False
                    new_message.deleted = False
                    _blacklist_control=db.session.query(BlackList).filter(BlackList.user_id==new_message.receiver_id).filter(BlackList.blacklisted_user_id==new_message.sender_id)
                    if _blacklist_control.first() is not None: #check if the user is in the blacklist of the receiver
                        print("blacklist rilevata")
                    else:
                        new_message.image= image_binary.decode('utf-8')
                        db.session.add(new_message)
            elif request.form['submit_button'] == 'Send as message':
                draft_message=db.session.query(Message).filter(Message.message_id==draft_id).first()
                draft_message.is_draft=False
                for nick in form.data['recipient']:
                    receiver_id = db.session.query(User).filter(User.nickname == nick)
                    draft_message.receiver_id = receiver_id.first().id
                draft_message.body=form.data['body']
                if form.data['delivery_date'] is None:
                        draft_message.delivery_date=date.today()
                else:
                    draft_message.delivery_date=form.data['delivery_date']
                #Does the creation date should be updated?
                draft_message.creation_date=date.today()
                _blacklist_control=db.session.query(BlackList).filter(BlackList.user_id==draft_message.receiver_id).filter(BlackList.blacklisted_user_id==draft_message.sender_id)
                if _blacklist_control.first() is not None:
                    #TODO add visula advice
                    print("blacklist rilevata")
                else:
                    draft_message.image= image_binary.decode('utf-8')
                    db.session.add(draft_message)
            elif request.form['submit_button'] == "Save changes":
                draft_message=db.session.query(Message).filter(Message.message_id==draft_id).first()
                for nick in form.data['recipient']:
                    receiver_id = db.session.query(User).filter(User.nickname == nick)
                    draft_message.receiver_id = receiver_id.first().id
                    draft_message.body=form.data['body']
                    if form.data['delivery_date'] is None:
                        draft_message.delivery_date=date.today()
                    else:
                        draft_message.delivery_date=form.data['delivery_date']
                    draft_message.image= image_binary.decode('utf-8')
                    db.session.add(draft_message)
            db.session.commit()
            q = db.session.query(User).filter(User.id == current_user.id)
            user_list = db.session.query(User.nickname).filter(User.id != current_user.id).filter(User.is_admin == False)
            new_user_list=[]
            for elem in user_list.all():
                new_user_list.append(str(elem).replace('(','').replace('\'', '').replace(')','').replace(',',''))
            dictUS = {}
            for el in new_user_list:
                    dictUS[el] = 0
            if draftReciever is not None:
                dictUS[draftReciever] = 1
            return render_template("send.html",  current_user=current_user, current_user_firstname=q.first().firstname, form=form, user_list=dictUS, is_submitted=True)
        
    else:
        #show the form and fill it if it's to modify a draft message
        if current_user is not None and hasattr(current_user, 'id'): #check if the user is logged
            form.body.data=draftBody
            user_list = db.session.query(User.nickname).filter(User.id != current_user.id).filter(User.is_admin == False)
            new_user_list=[]
            for elem in user_list.all():
                new_user_list.append(str(elem).replace('(','').replace('\'', '').replace(')','').replace(',',''))
            dictUS = {}
            for el in new_user_list:
                dictUS[el] = 0

            if (isReply is not None and isReply) and (draftReciever is not None):
                if draftReciever is not None:
                    form.body.data=str(draftReciever)+' wrote:\n'+str(draftBody)+'\n-----------------\n'

            if draft_id is not None:
                draft_message=db.session.query(Message).filter(Message.message_id==draft_id).first()
                form.body.data=draft_message.body
                form.delivery_date.data=draft_message.delivery_date
                dictUS[db.session.query(User).filter(User.id==draft_message.receiver_id).first().nickname] = 1

            q = db.session.query(User).filter(User.id == current_user.id)
            return render_template("send.html", current_user=current_user, current_user_firstname=q.first().firstname, form=form, user_list=dictUS, draft_id=draft_id), 200
        else:
            welcome = None
            return redirect('/login')

#This is the route to see user's information, to change it and to add word filter
@users.route('/profile', methods=['GET','POST'])
def profile():
    """
        This functionality allows to users to view the user's profile.
        Retrive the information about the user in the db, and pass as argument
        the values in the 'profile_info.html' template.
        If the user who try to access this service is not logged, will be render in the
        'home' page
    """
    if current_user is not None and hasattr(current_user, 'id'): #check if the user is logged
        if request.method == 'GET': #chow the form and the info
            user_filter_list = db.session.query(Filter_list).filter(Filter_list.user_id==current_user.id)
            if user_filter_list.first() is not None:
                return render_template("profile_info.html", current_user=current_user,user_filter_list=user_filter_list.first().list)
            else:
                return render_template("profile_info.html", current_user=current_user,user_filter_list="")
        elif request.method == 'POST': #apply the modification in the form
            if 'filter' in request.form: #if the user presses the filter button i change the word filter
                print("change filter branch")
                new_filter = Filter_list()
                new_filter.list = request.form['filter']
                new_filter.user_id = current_user.id
                user_filter_list = db.session.query(Filter_list).filter(Filter_list.user_id==current_user.id)
                if user_filter_list.first() is not None:
                    db.session.query(Filter_list).filter(Filter_list.user_id==current_user.id).delete()
                    db.session.add(new_filter)
                else:
                    db.session.add(new_filter)
                db.session.commit()
                return render_template("profile_info.html", current_user=current_user,user_filter_list=user_filter_list.first().list)
            else: #if the user presses the other button he changes is information with the info in the form
                print("change info branch")
                if check_password_hash(current_user.password, request.form['old_password']) : #check if the password that is put in the form is corrected
                    user_to_modify = db.session.query(User).filter(User.id==current_user.id).first()
                    user_to_modify.firstname = request.form['firstname']
                    user_to_modify.lastname = request.form['surname']
                    user_to_modify.date_of_birth = datetime.datetime.fromisoformat(request.form['birthday'])
                    user_to_modify.location = request.form['location']
                    if request.form['new_password']:
                        user_to_modify.password = generate_password_hash(request.form['new_password'])
                    db.session.commit()
                    print("info changed")
                else:
                    print("old password incorrect")
                user_filter_list = db.session.query(Filter_list).filter(Filter_list.user_id==current_user.id)
                if user_filter_list.first() is not None:
                    return render_template("profile_info.html", current_user=current_user,user_filter_list=user_filter_list.first().list)
                else:
                    return render_template("profile_info.html", current_user=current_user,user_filter_list="")
    else:
        return redirect('/login')

#This route is to delete an account 
@users.route('/deleteAccount', methods=['POST','GET'])
def delete_account():
    """
        This funcionality allows user to delete his/her account from MyMessageInTheBottle.
        The function will delete the account only for the logged user, and will redirect in the start page
    """
    if request.method == 'GET': #show the form
        if current_user is not None and hasattr(current_user, 'id'):
            return render_template("delete.html")
        else:
            return redirect('/login')
    else:
        if request.form['confirm_button'] == 'Delete my account': #if confirm_button is pressed the account is deleted (the elimination is done putting True in the is_deleted flag)
            if current_user is not None and hasattr(current_user, 'id'):
                query = db.session.query(User).filter(User.id == current_user.id)
                query.first().is_deleted=True
                db.session.commit()
                logout_user()
            return render_template('delete.html', is_deleted=True)
        else:
            return redirect('/')

#This route is to see the mailbox
@users.route('/mailbox', methods=['GET'])
def inbox():
    '''
        Shows the mailbox of the user divded into three parts
        1) The Inbox part shows the received messages
        2) The Sent part shows the messages that user sent
        3) The Draft part shows the messages in the draft

        It also provides the functionality for the user to delete future 
        messages if the user is lottery winner
    '''
    if current_user is not None and hasattr(current_user, 'id'): #check if the user is logged
        _sentMessages = db.session.query(Message,User).filter(Message.sender_id == current_user.id).filter(Message.is_draft == False).filter(Message.receiver_id==User.id).filter(Message.deleted==False)
        _filter_word = db.session.query(Filter_list).filter(Filter_list.user_id == current_user.id)
        _recMessages = db.session.query(Message,User).filter(Message.receiver_id == current_user.id).filter(Message.is_draft == False).filter(Message.sender_id==User.id).filter(Message.delivery_date<=date.today()).filter(Message.deleted==False)
        _draftMessage = db.session.query(Message,User).filter(Message.sender_id == current_user.id).filter(Message.is_draft == True).filter(Message.receiver_id==User.id)
        new_rec_list = [] 
        if _filter_word.first() is not None: #remove the messages that don't respect the filter word list
            print(_recMessages.all())
            for message in _recMessages.all():
                print(message)
                new_filter_word_list = _filter_word.first().list.split(',')
                control_flag = 0
                for elem in new_filter_word_list:
                    if elem != "":
                        if elem in message[0].body:
                            control_flag = 1
                if control_flag == 0:
                    new_rec_list.append(message)
                print(new_rec_list)
            return render_template("mailbox.html", messages=new_rec_list, sendMessages=_sentMessages.all(), draftMessages=_draftMessage.all())
        else:
            return render_template("mailbox.html", messages=_recMessages.all(), sendMessages=_sentMessages.all(), draftMessages=_draftMessage.all())
    else:
        return redirect('/login')

@users.route("/message/<id>", methods=["GET", "POST"])
def message_view(id):
    deletion = request.args.get("delete")
    lottery = request.args.get("lottery")
    print(deletion)
    if current_user is not None and hasattr(current_user, 'id'):
        if deletion != None and deletion:
            if lottery and current_user.lottery_points >= POINT_NECESSARY:
                query =  db.session.query(Message,User).filter(Message.message_id==id).filter(Message.sender_id == current_user.id).filter(Message.is_draft == False).filter(Message.receiver_id==User.id).filter(Message.deleted==False)
                if query.first() != None:
                    message=query.first()
                    current_user.lottery_points -= POINT_NECESSARY
                    message[0].deleted=True
                    db.session.commit()
                    return redirect("/mailbox")
            else:
                query =  db.session.query(Message,User).filter(Message.message_id==id).filter(Message.receiver_id == current_user.id).filter(Message.is_draft == False).filter(Message.receiver_id==User.id).filter(Message.deleted==False)
                if query.first() != None:
                    message=query.first()
                    if (not message[0].receiver_id == current_user.id) or (message[0].delivery_date>date.today()):
                        return 'You can\'t delete this message!'
                    else:
                        message[0].deleted=True
                        db.session.commit()
                        return 'Message deleted!'
                else:
                    return 'You can\'t delete this message!'
        else:
            # Received messages
            query =  db.session.query(Message,User).filter(Message.message_id==id).filter(Message.receiver_id == current_user.id).filter(Message.is_draft == False).filter(Message.sender_id==User.id).filter(Message.deleted==False)
            if query.first() != None:
                message=query.first()
                if message[0].receiver_id == current_user.id and message[0].delivery_date<=date.today():
                    if not message[0].opened:
                        message[0].opened = True
                        db.session.commit()
                    return render_template('message.html', message=message, mode='received')
            
            # Sent messages (DON'T FILTER FOR DELETED MESSAGES OTHERWISE THE SENDER KNOWS THAT THE MESSAGE IS DELETED BY THE RECIPIENT)
            query =  db.session.query(Message,User).filter(Message.message_id==id).filter(Message.sender_id == current_user.id).filter(Message.is_draft == False).filter(Message.receiver_id==User.id)
            if query.first() != None:
                message=query.first()
                if message[0].sender_id == current_user.id:
                    return render_template('message.html', message=message, mode='sent')
            else:
            	return 'You can\'t read this message!'
    else:
        return redirect('/login')

@users.route('/calendar')
def calendar():
    '''
        Shows sent and received messages to the user in the calendar.
    '''
    if current_user is not None and hasattr(current_user, 'id'):
        _sentMessages = db.session.query(Message,User).filter(Message.sender_id == current_user.id).filter(Message.is_draft == False).filter(Message.receiver_id==User.id)
        _recMessages = db.session.query(Message,User).filter(Message.receiver_id == current_user.id).filter(Message.is_draft == False).filter(Message.sender_id==User.id).filter(Message.delivery_date<=date.today()).filter(Message.deleted==False)

        # Contains a list of dict [{'todo' : 'Title'}, {'date' : 'date'}, {'msgID' : 'messageID'}]
        events = []

        for message in _sentMessages:
            events.append({'todo' : "Sent: " + str(message[1].nickname), 'date' : str(message[0].delivery_date), 'msgID' : str(message[0].message_id)})

        for message in _recMessages:
            events.append({'todo' : "Received: " + str(message[1].nickname), 'date' : str(message[0].delivery_date), 'msgID' : str(message[0].message_id)})

        return render_template('calendar.html', events = events)
    else:
        return redirect('/login')

@users.route("/lottery", methods=["GET","POST"])
def lottery():
    ''' 
        The user can partecipate to the monthly lottery
    '''
    if current_user is not None and hasattr(current_user, 'id'):
        # asking if the user is already a participant of the lottery
        lottery_query=db.session.query(Lottery).filter(Lottery.contestant_id == current_user.id).all()

        if request.method == "POST":
                if(not lottery_query):
                    new_contestant = Lottery()
                    new_contestant.contestant_id = current_user.id
                    print("User added to lottery db:" + str(current_user.id) )
                    db.session.add(new_contestant)
                    db.session.commit()

                    flash("You're partecipating to the lottery!")
                    return redirect("/mailbox")
                else:
                    flash("You're already partecipating to the lottery!")
                    return redirect("/mailbox")
        elif request.method == "GET":
                is_partecipating = 1
                if(not lottery_query):
                    is_partecipating = 0
                return render_template("lottery.html", is_partecipating = is_partecipating)
    else:
        return redirect('/login') 

#This is the route to delete a message
@users.route("/delete_messages", methods=["GET","POST"])
def delete_message():
    if current_user is not None and hasattr(current_user, 'id'): #check if the user is logged
        if current_user.lottery_points >= POINT_NECESSARY:
            _futureMessages = db.session.query(Message,User).filter(Message.sender_id == current_user.id).filter(Message.is_draft == False).filter(Message.delivery_date>date.today()).filter(Message.deleted==False).filter(Message.receiver_id==User.id)
            return render_template("delete_messages.html", futureMessages = _futureMessages.all()), 201
        else:
            return redirect('/mailbox')
    else:
        return redirect('/login')
