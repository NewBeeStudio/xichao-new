# -*- coding: utf-8 -*-
from flask import Flask,request,session
from database import db_session
import os
from flask_wtf.csrf import CsrfProtect
from datetime import datetime
from hashlib import md5
from flask.ext.login import LoginManager
from itsdangerous import URLSafeTimedSerializer
from datetime import timedelta
from flask.ext.login import current_user


app = Flask(__name__)



# 配置，之后可以考虑单独放在一个文件中
SECRET_KEY = '\x18\xd1\x81cU\xb9j%\xb9\x00\xf5\xf3\xe9r\xcb\x82lq\x9e\xa8\xe3\x14@\x96'
DEBUG = True


#Jinja2过滤器配置
#获取日期: 2014-02-02 xx:xx:xx—> 14-02-02
@app.template_filter('time_split')
def time_split_filter(s):
    return str(s).split(' ')[0][2:]

#获取日期: 2014-02-02 xx:xx:xx—> 2014-02-02
@app.template_filter('time_split_2')
def time_split_filter_2(s):
    return str(s).split(' ')[0]

#获取日期: 2014-02-02 xx:xx:xx—> 2014年2月2日 xx:xx
@app.template_filter('time_split_3')
def time_split_filter_3(s):
    (date, time) = str(s).split(' ') #2014-02-02
    date = date.split('-')
    time = time.split(':')
    return date[0] + u'年' + date[1] + u'月' + date[2] + u'日  ' + time[0] + ':' + time[1]


#获取日期: 2014-02-02 xx:xx:xx—> 2014年2月
@app.template_filter('time_split_4')
def time_split_filter_4(s):
    date = str(s).split(' ')[0].split('-') #2014-02-02
    return date[0] + u'年' + date[1] + u'月'

#获取日期: 2014-02-02 xx:xx:xx—> 2014年2月2日 xx:xx
@app.template_filter('time_split_5')
def time_split_filter_5(s):
    (date, time) = str(s).split(' ') #2014-02-02
    date = date.split('-')
    time = time.split(':')
    return date[1] + u'月' + date[2] + u'日  ' + time[0] + ':' + time[1]

#获取日期: 2014-02-02 xx:xx:xx—> 2014-02-02
@app.template_filter('time_split_6')
def time_split_filter_2(s):
    return '.'.join(str(s).split(' ')[0].split('-'))

#zip
@app.template_filter('zip')
def zip_filter(s):
    return zip(range(1,len(s)+1), s)


#flask-login登陆配置
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message = u"请先登录"
login_manager.session_protection = "strong"
login_manager.init_app(app)
login_serializer = URLSafeTimedSerializer(SECRET_KEY)
import views
import admins
# cookie和session持续时间
PERMANENT_SESSION_LIFETIME = timedelta(minutes=20)
REMEMBER_COOKIE_DURATION = timedelta(days=7)


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
HOST_NAME='xichao-o.com'

#文章题图路径
ARTICLE_TITLE_DEST = os.path.join(os.path.dirname(__file__), 'upload/article/article_title')
#文章内容图片路径
ARTICLE_CONTENT_DEST = os.path.join(os.path.dirname(__file__), 'upload/article/article_content')
#活动内容图片路径
ACTIVITY_CONTENT_DEST = os.path.join(os.path.dirname(__file__), 'upload/activity/activity_content')
#活动题图路径
ACTIVITY_TITLE_DEST = os.path.join(os.path.dirname(__file__), 'upload/activity/activity_title')

#专栏图片路径
SPECIAL_DEST=os.path.join(os.path.dirname(__file__),'upload/special')
#书籍图片路径
BOOK_PICTURE_DEST=os.path.join(os.path.dirname(__file__),'upload/book')

#首页图片路径
HOMEPAGE_DEST=os.path.join(os.path.dirname(__file__),'upload/homepage')

DEFAULT_ARTICLE_TITLT_IMAGE=['article_upload_pic_1.jpg','article_upload_pic_2.jpg','article_upload_pic_3.jpg','article_upload_pic_4.png','article_upload_pic_5.jpg','article_upload_pic_6.jpg']




app.config.from_object(__name__)




##############################  csrf  ##################################
##ueditor文章内容图片上传临时过滤
@app.before_request
def csrf_protect():
    if not current_user.is_anonymous():
        if current_user.role==3:
            pass
        else:
            if request.method=="POST" and request.path!="/editor/article":
                if not session['_csrf_token'] or request.form['_csrf_token']!=session['_csrf_token']:
                    abort(403)
    else:
        if request.method=="POST":
            if not session['_csrf_token'] or request.form['_csrf_token']!=session['_csrf_token']:
                abort(403)

'''
    if request.method == "POST" and request.path!="/login" and request.path!="/register" and request.path!="/upload/avatar" and request.path!="/editor/article" and request.path!="/forgetPassword" and current_user.role!=3:

        if not session['_csrf_token'] or request.form['_csrf_token']!=session['_csrf_token']:
            abort(403)
'''

def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = md5(SECRET_KEY + datetime.now().strftime('%Y%m%d%H%M%S')).hexdigest()
    return session['_csrf_token']

app.jinja_env.globals['csrf_token'] = generate_csrf_token 


###############################  db_session  ###########################
@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()
