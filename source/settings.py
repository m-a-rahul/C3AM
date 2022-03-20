import production_config

DEBUG = True
MONGO_CLIENT_URL = production_config.MONGO_CLIENT_URL
MAIL_USERNAME = production_config.MAIL_USERNAME
MAIL_PASSWORD = production_config.MAIL_PASSWORD

if DEBUG:
    MONGO_CLIENT_URL = 'mongodb://localhost:5000/'
    MAIL_USERNAME = 'noreply.c3am.dev@gmail.com'
    MAIL_PASSWORD = '4mrDDT7B>(=B'
