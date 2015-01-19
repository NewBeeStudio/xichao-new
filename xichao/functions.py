# -*- coding: utf-8 -*-
'''

	功能函数模块

	实现一些数据库基本的功能，被高层次代码所调用

'''
from xichao import app
from hashlib import md5
from models import User,Article,Special,Book,Comment
from database import db_session
from flask import jsonify,render_template,request,session
from sqlalchemy import or_, not_, and_, desc
from werkzeug import secure_filename
from datetime import datetime
from flask.ext.mail import Mail
from flask.ext.mail import Message


##################################  注册函数  ####################################
def nick_exist(nick):
	result=db_session.query(User).filter_by(nick=nick).all()
	if len(result)>0:
		return True
	else:
		return False

def email_exist(email):
	result=db_session.query(User).filter_by(email=email).all()
	if len(result)>0:
		return True
	else:
		return False

def encrypt(password):
	encrypt_password=md5(password).hexdigest()
	return encrypt_password

ALLOWED_EXTENSIONS=['jpg']
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS

def get_state(nick,password):
	result=db_session.query(User).filter(and_(User.nick==nick,User.password==password)).all()
	if len(result)>0:
		return result[0].state
	else:
		return False
def update_state(nick):
	db_session.query(User).filter(User.nick==nick).update({'state':'1'})
	db_session.commit()

def get_secure_photoname(filename):
	secured_filename=secure_filename(filename)
	photoname=secured_filename.rsplit('.',1)[0]+datetime.now().strftime('%Y%m%d%H%M%s')+'.'+secured_filename.rsplit('.',1)[1]
	return photoname

def send_verify_email(nick,password,email):
	verify_url=app.config['HOST_NAME']+'/verify?nick='+nick+'&secret='+encrypt(password)
	mail=Mail(app)
	msg=Message(u'曦潮书店',sender='xichao_test@163.com',recipients=[email])
	msg.body='text body'
	msg.html = render_template('test_verify_email.html',verify_url=verify_url)
	with app.app_context():
		mail.send(msg)
##################################  登陆函数  ####################################
def get_nick(email,password):
	result=db_session.query(User).filter(and_(User.email==email,User.password==encrypt(password))).all()
	if len(result)>0:
		return result[0].nick
	else:
		return False
##################################  文章函数  ####################################
def new_draft(userid = None):
    ## 新建草稿，返回值为新的article_id
    from models import Article
    article = Article(title = u"草稿", picture = u"草稿",
                      content = "空", is_draft = '1',
                      time = datetime.now(), category = '0',    ## 0表示 TODO 1表示 TODO 2 表示 TODO
                      groups = '1', user_id = userid,             ## 1表示 TODO
                      book_id = 1, special_id = 1)
    db_session.add(article)
    db_session.commit()
    
    # TODO 查询新插入的article_id并返回
    return 2

#文章分页显示函数
def get_article_pagination(page,posts_per_page):
	pagination=db_session.query(Article).paginate(page,posts_per_page,False)#获得分页对象
	return pagination
	#pagination.items是分页好的数据
'''
<div class="pagination  "> 
    <div class="row-fluid"> 
        <div class="span3 offset2"> 
            {% if pagination.has_prev %} 
                <a href="/index/{{ pagination.prev_num }}">previous</a> 
            {% endif %} 
        </div> 
        <div class="span3 "> 
            <a href="">Page {{ pagination.page }} of {{ pagination.pages }}.</a> 
        </div> 
        <div class="span3 ">

            {% if pagination.has_next %} 
                <a href="/index/{{ pagination.next_num }}">next</a> 
            {% endif %} 
        </div> 
    </div> 
</div>
'''
#返回1个元组，result[0][0]是Article类的数据库实例，result[0][1]是该Article实例所对应的User.nick,是字符串,result[0][2]是该Article实例所对应的Book实例
def get_article_information(article_id):
	result=db_session.query(Article,User.nick,Book).join(User,Book).filter(Article.article_id==article_id).all()
	#result[0][0]
	#result[0][1]
	#result[0][2]
	print result[0]
	if len(result)>0:
		return result[0]
	else:
		return None

#返回一个列表，列表中的元素为元组，result[x][0]是Comment类的数据库实例，result[x][1]是该Comment所对应的用户昵称
def get_article_comment(article_id):
	result=db_session.query(Comment,User.nick).join(User).filter(Comment.article_id==article_id).order_by(desc(Comment.time)).all()
	return result
##################################  专栏函数  ####################################
def get_special_information(special_id):
	result=db_session.query(Special,User.nick).join(User).filter(Special.special_id==special_id).all()
	if len(result)>0:
		return result[0]
	else:
		return None
	
def get_special_article(special_id,page_id):
	pagination=db_session.query(Article).filter_by(special_id=special_id).paginate(page_id,5,False)
	return pagination
