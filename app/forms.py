from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, BooleanField, StringField, TextAreaField, \
    IntegerField, SelectField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField

from data import User, create_session


def validator_lower(form, field):
    if field.data != field.data.lower():
        raise ValidationError('Field must be lowercase')


def validator_password(form, field):
    password = field.data
    if len(password) <= 8:
        raise ValidationError('Password must be longer')
    if not (''.join(filter(lambda x: x.isupper() and x.isalpha(), password)) and
            ''.join(filter(lambda x: x.islower() and x.isalpha(), password))):
        raise ValidationError('Password does not contain uppercase or lowercase letters')
    if not ''.join(filter(lambda x: x.isdigit(), password)):
        raise ValidationError('Password does not contain digits')
    keyboard = 'qwertyuiop\nasdfghjkl\nzxcvbnm\nйцукенгшщзхъ\nфывапролджэё\nячсмитьбю'
    for i in range(len(password) - 2):
        if password[i:i + 3].lower() in keyboard:
            raise ValidationError('Password is too easy')


def validator_nickname_unique(form, field):
    session = create_session()
    if session.query(User).filter(User.nickname == field.data).first():
        raise ValidationError('Nickname already registered')


def validator_email_unique(form, field):
    session = create_session()
    if session.query(User).filter(User.email == field.data).first():
        raise ValidationError('Email already registered')


class LoginForm(FlaskForm):
    email = EmailField('Login/email', validators=[DataRequired(), Email(), validator_lower])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign in')


class RegisterForm(FlaskForm):
    email = EmailField('Login/email', validators=[DataRequired(), Email(), validator_lower,
                                                  validator_email_unique])
    password = PasswordField('Password', validators=[DataRequired(), validator_password])
    password_again = PasswordField('Repeat password', validators=[
        EqualTo("password", message="Passwords do not match")])
    nickname = StringField('Nickname', validators=[DataRequired(), validator_nickname_unique])
    name = StringField('Name', validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])
    submit = SubmitField('Sign up')
