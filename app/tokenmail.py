from flask import url_for
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer

from app import app, mail


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])


def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except:
        return False
    return email


def send_mail_to_certify(user):
    token = generate_confirmation_token(user.email)

    url_for_user = url_for('blueprint_pages.email_certify', token=token, _external=True)
    with app.app_context():
        certify_message = Message(
            "Auto-email confirmation - User certify",
            recipients=[user.email],
            sender=app.config['MAIL_DEFAULT_SENDER'],
            body=f'To confirm your account go to the link: {url_for_user}')
        mail.send(certify_message)
