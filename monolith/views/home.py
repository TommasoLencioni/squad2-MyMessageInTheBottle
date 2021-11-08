from flask import Blueprint, render_template, redirect

from monolith.auth import current_user

home = Blueprint('home', __name__)


@home.route('/')
def index():
    '''
        Redirects the user to the home page (mailbox in our case) if the user
        successfully logged in.
    '''
    if current_user is not None and hasattr(current_user, 'id'):
        welcome = "Logged In!"
    else:
        welcome = None
    return redirect("/mailbox")
