import wtforms as f
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from datetime import date

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

    def validate_on_submit(self):
            result = super(UserForm, self).validate()
            print(str(self.date_of_birth.data)+"data")
            if (self.date_of_birth.data is not None and self.date_of_birth.data>date.today()):
                return False
            else:
                return result

class SendForm(FlaskForm):
    recipient = f.StringField('Recipient', validators=[DataRequired()])
    body = f.TextAreaField('Message', validators=[DataRequired()])
    delivery_date = f.DateField('Delivery date', format='%d/%m/%Y')
    send_button = f.SubmitField('send')
    draft_button = f.SubmitField('save as draft')
    display = ['recipient', 'body', 'delivery_date']