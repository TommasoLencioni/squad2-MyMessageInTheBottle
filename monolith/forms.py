import wtforms as f
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    email = f.StringField('email', validators=[DataRequired()])
    password = f.PasswordField('password', validators=[DataRequired()])
    display = ['email', 'password']


class UserForm(FlaskForm):
    email = f.StringField('email', validators=[DataRequired()])
    firstname = f.StringField('firstname', validators=[DataRequired()])
    lastname = f.StringField('lastname', validators=[DataRequired()])
    password = f.PasswordField('password', validators=[DataRequired()])
    date_of_birth = f.DateField('date_of_birth', format='%d/%m/%Y')
    nickname = f.StringField('nickname', validators=[DataRequired()])
    location = f.StringField('location', validators=[DataRequired()])
    display = ['email', 'firstname', 'lastname', 'password', 'date_of_birth','nickname','location']

class SendForm(FlaskForm):
    recipient = f.StringField('Recipient', validators=[DataRequired()])
    body = f.TextAreaField('Message', validators=[DataRequired()])
    delivery_date = f.DateField('Delivery date', format='%d/%m/%Y')
    display = ['recipient', 'body', 'delivery_date']