# -*- coding: utf-8 -*-
from flask import Flask,request,session
from database import db_session
import os
from flask_wtf.csrf import CsrfProtect
from datetime import datetime
from hashlib import md5

app = Flask(__name__)
import views

# 配置，之后可以考虑单独放在一个文件中
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

#头像路径
PHOTO_DEST=os.path.join(os.path.dirname(__file__),'upload/avator')
#主机地址
HOST_NAME='http://127.0.0.1:5000'

#文章题图路径
ARTICLE_TITLE_DEST = os.path.join(os.path.dirname(__file__), 'upload/article/article_title')
#文章内容图片路径
ARTICLE_CONTENT_DEST = os.path.join(os.path.dirname(__file__), 'upload/article/article_content')


app.config.from_object(__name__)


##############################  csrf  ##################################

@app.before_request
def csrf_protect():
    if request.method == "POST":
        token = session.pop('_csrf_token', None)
#        if not token or token != request.form.get('_csrf_token'):
#            abort(403)
def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = md5(SECRET_KEY + datetime.now().strftime('%Y%m%d%H%M%s')).hexdigest()
    return session['_csrf_token']

app.jinja_env.globals['csrf_token'] = generate_csrf_token 


###############################  db_session  ###########################
@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()
