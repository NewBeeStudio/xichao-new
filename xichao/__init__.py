# -*- coding: utf-8 -*-
from flask import Flask
from database import db_session

app = Flask(__name__)
import views

# 配置，之后可以考虑单独放在一个文件中
CSRF_ENABLED = True
SECRET_KEY = '\x18\xd1\x81cU\xb9j%\xb9\x00\xf5\xf3\xe9r\xcb\x82lq\x9e\xa8\xe3\x14@\x96'
DEBUG = True


# email server
MAIL_SERVER = 'smtp.163.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = 'xichao_test'
MAIL_PASSWORD = 'xichaoxichao'

# administrator list
ADMINS = ['xichao_test@163.com']

MAX_CONTENT_LENGTH=16*1024*1024


app.config.from_object(__name__)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()