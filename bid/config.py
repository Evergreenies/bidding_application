from os import environ

SECRET_KEY = ''

# TODO: Database configuration
USERNAME = 'username'
PASSWORD = ''
HOST = '127.0.0.1'
DATABASE = 'bidder_database'

SQLALCHEMY_DATABASE_URI = f'mysql://{USERNAME}:{PASSWORD}@{HOST}/{DATABASE}'
SQLALCHEMY_TRACK_MODIFICATIONS = True

# TODO: Email configuration
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True

MAIL_USERNAME = environ.get('EMAIL_USER')
MAIL_PASSWORD = environ.get('EMAIL_PASSWORD')
