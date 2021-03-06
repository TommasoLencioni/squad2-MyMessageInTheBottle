from flask import Blueprint, redirect, render_template,flash
from flask_login import login_user, logout_user, current_user

from monolith.database import User, db
from monolith.forms import LoginForm
from monolith.views.users import create_user

auth = Blueprint('auth', __name__)

LOGIN_OK = 200
LOGIN_FAIL = 201
DOUBLE_LOGIN = 202

#This is the route to do the login, in the login.html page there is a form and the information 
#that are put in the form are cheked in the db and the is_active flag in the db is put equal to True
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if not (current_user is not None and hasattr(current_user, 'id')):
        form = LoginForm()
        email, password = form.data['email'], form.data['password']
        q = db.session.query(User).filter(User.email == email).filter(User.is_deleted==False)
        user = q.first()
        if user is not None and user.authenticate(password):
            user.is_active=True
            db.session.commit()
            login_user(user)
            return render_template("mailbox.html"), LOGIN_OK
        else:
            flash("Incorrect password or username.")        
            return render_template('login.html', form=form), LOGIN_FAIL
    else:
        return "You are currently logged in, you have to <a href=/logout>logout</a> first" , DOUBLE_LOGIN

#This is the route to do the logout, the flag is_active of the use in the db is put equal to False
@auth.route("/logout")
def logout():
    if current_user is not None and hasattr(current_user, 'id'):
        q = db.session.query(User).filter(User.id==current_user.id)
        user = q.first()
        user.is_active=False
        db.session.commit()
        logout_user()
        return redirect('/')
    else:
        return redirect('/login')
