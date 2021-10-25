from flask import Blueprint, redirect, render_template
from flask_login import login_user, logout_user, current_user

from monolith.database import User, db
from monolith.forms import LoginForm
from monolith.views.users import create_user

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email, password = form.data['email'], form.data['password']
        q = db.session.query(User).filter(User.email == email)
        user = q.first()
        if user is not None and user.authenticate(password):
            user.is_active=True
            db.session.commit()
            login_user(user)
            return redirect('/')
    return render_template('login.html', form=form)

@auth.route("/logout")
def logout():
    q = db.session.query(User).filter(User.firstname==current_user.firstname)
    user = q.first()
    user.is_active=False
    db.session.commit()
    logout_user()
    return redirect('/')
