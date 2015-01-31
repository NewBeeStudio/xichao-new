# -*- coding: utf-8 -*-
'''

	功能函数模块

	实现一些数据库基本的功能，被高层次代码所调用

'''
from xichao import app
from hashlib import md5
from models import User,Article,Special,Book,Comment,Article_session,Activity_session,Activity,Comment_activity,Collection_Special,Collection_User
from database import db_session
from flask import jsonify,render_template,request,session
from sqlalchemy import or_, not_, and_, desc
from werkzeug import secure_filename
from datetime import datetime
from flask.ext.mail import Mail
from flask.ext.mail import Message
from flask.ext.sqlalchemy import Pagination
import re
#from sqlalchemy.orm import query


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
	photoname=secured_filename.rsplit('.',1)[0]+datetime.now().strftime('%Y%m%d%H%M%S')+'.'+secured_filename.rsplit('.',1)[1]
	return photoname

def send_verify_email(nick,password,email):
	verify_url=app.config['HOST_NAME']+'/verify?nick='+nick+'&secret='+encrypt(password)
	mail=Mail(app)
	msg=Message(u'曦潮书店',sender='xichao_test@163.com',recipients=[email])
	msg.body='text body'
	msg.html = render_template('test_verify_email.html',verify_url=verify_url)
	with app.app_context():
		try:
			mail.send(msg)
		except:
			pass

##################################  登陆函数  ####################################
def get_nick(email,password):
	result=db_session.query(User).filter(and_(User.email==email,User.password==encrypt(password))).all()
	if len(result)>0:
		return result[0].nick
	else:
		return False

##################################  忘记/重设密码 #################################
#通过email获取nick
def get_nick_by_email(email):
	nick = db_session.query(User.nick).filter_by(email=email).first()
	return nick[0]

#通过email获取password
def get_password_by_email(email):
	password = db_session.query(User.password).filter_by(email=email).first()
	return password[0]

#发送重设密码邮件
def send_resetpassword_email(nick,password,email):
	verify_url=app.config['HOST_NAME']+'/resetPassword/'+nick+'/'+password #/nick/MD5(password)
	mail=Mail(app)
	msg=Message(u'重置曦潮网站的密码',sender='xichao_test@163.com',recipients=[email])
	msg.body='text body'
	msg.html = render_template('test_verify_email.html',verify_url=verify_url)
	with app.app_context():
		try:
			mail.send(msg)
		except:
			pass

#是否存在该用户名，用户名和密码是否匹配
def check_nickpassword_match(nick, password):
	pw = db_session.query(User.password).filter_by(nick=nick).all()
	if not len(pw): #不存在nick
		return False 
	elif pw[0][0] != password:
		return False
	else:
		return True

#更新密码
def update_password(nick, password):
	user = db_session.query(User).filter_by(nick=nick).scalar()
	user.password = encrypt(password)
	db_session.commit()

##################################  文章函数  ####################################
def get_article_session_id():
    article_session = Article_session()
    db_session.add(article_session)
    db_session.commit()
    result=db_session.query(Article_session.article_session_id).order_by(desc(Article_session.article_session_id)).first()
    return result[0]
def get_activity_session_id():
	activity_session=Activity_session()
	db_session.add(activity_session)
	db_session.commit()
	result=db_session.query(Activity_session.activity_session_id).order_by(desc(Activity_session.activity_session_id)).first()
	return result[0]

#添加文章
def create_article(title,content,title_image,article_session_id,is_draft,user_id,group_id,category_id,abstract,book_id):
	result=db_session.query(Article).filter_by(article_session_id=article_session_id).all()
	if len(result)>0:
		article=db_session.query(Article).filter_by(article_session_id=article_session_id).scalar()
		article.title=title
		article.content=content
		article.picture=title_image
		article.time=datetime.now()
		article.is_draft=is_draft
		article.abstract=abstract
		article.book_id=book_id
		db_session.commit()
		return result[0].article_id
	else:
		article=Article(title=title,content=content,picture=title_image,time=datetime.now(),user_id=user_id,article_session_id=article_session_id,is_draft=is_draft,groups=group_id,category=category_id,abstract=abstract,book_id=book_id)
		db_session.add(article)
		db_session.commit()
		result=db_session.query(Article).filter_by(article_session_id=article_session_id).first()
		return result.article_id

def create_book(book_picture,book_author,book_press,book_page_num,book_price,book_press_time,book_title,book_ISBN,book_binding):
	result=db_session.query(Book).filter_by(ISBN=book_ISBN).all()
	if len(result)>0:
		book=db_session.query(Book).filter_by(ISBN=book_ISBN).scalar()
		book.favor+=1
		db_session.commit()
		return result[0].book_id
	else:
		book=Book(title=book_title,ISBN=book_ISBN,picture=book_picture,author=book_author,press=book_press,page_num=book_page_num,price=book_price,press_time=book_press_time,binding=book_binding)
		db_session.add(book)
		db_session.commit()
		result=db_session.query(Book).filter_by(ISBN=book_ISBN).first()
		return result.book_id

def create_activity(title,content,title_image,activity_session_id,activity_time):
	result=db_session.query(Activity).filter_by(activity_session_id=activity_session_id).all()
	if len(result)>0:
		activity=db_session.query(Activity).filter_by(activity_session_id=activity_session_id).scalar()
		activity.name=title
		activity.content=content
		activity.picture=title_image
		activity.create_time=datetime.now()
		activity.activity_time=activity_time
		db_session.commit()
	else:
		activity=Activity(name=title,content=content,picture=title_image,create_time=datetime.now(),activity_session_id=activity_session_id,activity_time=activity_time)
		db_session.add(activity)
		db_session.commit()

def get_user_id(nick):
	user_id=db_session.query(User.user_id).filter_by(nick=nick).first()
	return user_id[0]

#文章分页显示函数
def get_article_pagination(page,posts_per_page):
	pagination=db_session.query(Article).paginate(page,posts_per_page,False)#获得分页对象
	return pagination
	#pagination.items是分页好的数据

#返回1个元组，result[0][0]是Article类的数据库实例，result[0][1]是该Article实例所对应的User.nick,是字符串,result[0][2]是该Article实例所对应的Book实例
def get_article_information(article_id):
	result=db_session.query(Article,User.nick,Book).join(User,Book).filter(Article.article_id==article_id).all()
	#print result[0]
	if len(result)>0:
		return result[0]
	else:
		return None

def get_activity_information(activity_id):
	result=db_session.query(Activity).filter_by(activity_id=activity_id).all()
	if len(result)>0:
		return result[0]
	else:
		return None

#返回一个列表，列表中的元素为元组，result[x][0]是Comment类的数据库实例，result[x][1]是该Comment所对应的用户昵称,result[x][2]是该Comment所对应的用户头像
def get_article_comments(article_id):
	result=db_session.query(Comment,User.nick,User.photo).join(User,Comment.user_id==User.user_id).filter(Comment.article_id==article_id).order_by(desc(Comment.time)).all()
	if len(result)>0:
		return result
	else:
		return None

def get_activity_comments(activity_id):
	result=db_session.query(Comment_activity,User.nick,User.photo).join(User,Comment_activity.user_id==User.user_id).filter(Comment_activity.activity_id==activity_id).order_by(desc(Comment_activity.time)).all()
	if len(result)>0:
		return result
	else:
		return None

def update_read_num(article_id):
	article=db_session.query(Article).filter_by(article_id=article_id).scalar()
	article.read_num+=1
	db_session.commit()


def update_read_num_activity(activity_id):
	activity=db_session.query(Activity).filter_by(activity_id=activity_id).scalar()
	activity.read_num+=1
	db_session.commit()
##################################  专栏函数  ####################################
def paginate(query,page,per_page=20,error_out=True):
	if error_out and page < 1:
		abort(404)
	items = query.limit(per_page).offset((page - 1) * per_page).all()
	if not items and page != 1 and error_out:
		abort(404)
	if page == 1 and len(items) < per_page:
		total = len(items)
	else:
		total = query.order_by(None).count()
	return Pagination(query, page, per_page, total, items)


def get_special_author(userid):
    result = db_session.query(User).filter_by(user_id = userid)
    return result[0]

def get_special_information(special_id):
#	result=db_session.query(Special,User.nick).join(User).filter(Special.special_id==special_id).all()
    result = db_session.query(Special).filter_by(special_id = special_id).all()
    if len(result)>0:
        return result[0]
    else:
        return None

def get_special_article(special_id, page_id, sort):
    if sort == "time":
        query = db_session.query(Article).filter_by(special_id = special_id).order_by(Article.time.desc())
    else:
        query = db_session.query(Article).filter_by(special_id = special_id).order_by(Article.favor.desc())

    pagination = paginate(query = query, page = page_id, per_page = 5, error_out = True)
    return pagination
    
def get_special_author_other(user_id):
    query = db_session.query(Special.name).filter_by(user_id = user_id).all()
    return query

###################################  昵称函数  ####################################
def getNick():
	nick=None
	if 'user_id' in session:
		result = db_session.query(User.nick).filter_by(user_id=int(session['user_id'])).first()
		nick = result[0]
	
	# nick = None
	# if 'user' in session:
	# 	nick = session['user']
	# elif request.cookies.get('user')!=None:
	# 	nick = request.cookies.get('user')
	return nick

###################################  头像函数  ####################################
def get_avatar():
	nick=getNick()
	avatar=db_session.query(User.photo).filter_by(nick=nick).first()
	return avatar[0]
###################################  评论函数  ####################################
def create_comment(content,to_user_id,article_id):
	user_id=int(session['user_id'])
	comment=Comment(article_id=article_id,content=content,user_id=user_id,to_user_id=to_user_id,time=datetime.now())
	db_session.add(comment)
	db_session.commit()
def update_comment_num(article_id):
	article=db_session.query(Article).filter_by(article_id=article_id).scalar()
	article.comment_num+=1
	db_session.commit()

def create_activity_comment(content,activity_id):
	user_id=int(session['user_id'])
	comment_activity=Comment_activity(activity_id=activity_id,content=content,user_id=user_id,time=datetime.now())
	db_session.add(comment_activity)
	db_session.commit()
def update_activity_comment_num(activity_id):
	activity=db_session.query(Activity).filter_by(activity_id=activity_id).scalar()
	activity.comment_num+=1
	db_session.commit()


###################################  获取文章摘要函数  ###############################
def get_abstract_plain_text(abstract):
	img_list=re.findall('<img.*?>',abstract)
	for img_r in img_list:
		abstract=abstract.replace(img_r,'')
	return abstract


###################################  分页函数  ######################################
##源自官方的实现
def paginate(query,page,per_page=20,error_out=True):
	if error_out and page < 1:
		abort(404)
	items = query.limit(per_page).offset((page - 1) * per_page).all()
	if not items and page != 1 and error_out:
		abort(404)
	if page == 1 and len(items) < per_page:
		total = len(items)
	else:
		total = query.order_by(None).count()
	return Pagination(query, page, per_page, total, items)
###################################  获取文章组函数  #################################
def get_article_pagination_by_favor(group_id,category_id,page_id):
	query=db_session.query(Article).filter(and_(Article.groups==group_id,Article.category==category_id)).order_by(desc(Article.favor))
	return paginate(query,page_id,5,False)
def get_article_pagination_by_time(group_id,category_id,page_id):
	query=db_session.query(Article).filter(and_(Article.groups==group_id,Article.category==category_id)).order_by(desc(Article.time))
	return paginate(query,page_id,5,False)
	
	
##################################  收藏专栏  ####################################
def collection_special(user_id, special_id):
    query = db_session.query(Collection_Special).filter_by(user_id = user_id, special_id = special_id).all()
    if len(query) == 0:
        collect_spe = Collection_Special(user_id = user_id, 
                                         special_id = special_id,
                                         time = datetime.now())
        db_session.add(collect_spe)
        db_session.commit()
    else:
        raise Exception
        
##################################  收藏专栏作家  ####################################
def collection_special_author(user_id, special_id):
    query = db_session.query(Special).filter_by(special_id = special_id).all()
    another_user_id = query[0].user_id
    if (user_id == another_user_id):
        return "self"
    query = db_session.query(Collection_User).filter_by(user_id = user_id, another_user_id = another_user_id).all()
    if len(query) == 0:
        collect_usr = Collection_User(user_id = user_id, 
                                      another_user_id = another_user_id,
                                      time = datetime.now())
                                      #用户user_id 收藏用户 another_user_id
        db_session.add(collect_usr)
        db_session.commit()
    else:
        return "already"
    return "success"

##################################  获取用户角色函数  ####################################
def get_role(user_id):
	result=db_session.query(User.role).filter_by(user_id=user_id).first()
	return result[0]


def get_user_by_nick(nick):
	result=db_session.query(User).filter_by(nick=nick).first()
	return result

def examine_user_id(user_id):
	result=db_session.query(User).filter_by(user_id=user_id).all()
	if len(result)>0:
		return True
	else:
		return False
def create_user_collection(another_user_id,user_id):
	collection=Collection_User(user_id=user_id,another_user_id=another_user_id,time=datetime.now())
	db_session.add(collection)
	db_session.commit()

def get_hot_ground_acticle():
	result=db_session.query(Article,User.nick).join(User).filter(Article.groups=='1').order_by(desc(Article.coins)).limit(10).all()
	return result

def get_article_group_by_coin(groups,category):
	result=db_session.query(Article,User.nick).join(User).filter(and_(Article.groups==groups,Article.category==category)).order_by(desc(Article.coins)).limit(10).all()
	return result
