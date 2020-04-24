import os


class Config:
    APP_ROOT = os.path.abspath(os.curdir)
    SECRET_KEY = 'key_secret_a_lot'
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USE_TLS = False
    MAIL_USERNAME = 'technobotforum@gmail.com'
    MAIL_DEFAULT_SENDER = 'technobotforum@gmail.com'
    MAIL_PASSWORD = 'OGOPAROL1ok'
    SECURITY_PASSWORD_SALT = 'my_precious_two'

