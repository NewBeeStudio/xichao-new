# -*- coding: utf-8 -*-
'''

	功能函数模块

	实现一些数据库基本的功能，被高层次代码所调用

'''
from xichao import app
from hashlib import md5
from models import User,Article,Special,Book,Comment,Article_session,Activity_session,Activity,Comment_activity,Collection_Special,Collection_User,Collection_Article,Collection_Activity
from database import db_session
from flask import jsonify,render_template,request,session
from sqlalchemy import or_, not_, and_, desc
from werkzeug import secure_filename
from datetime import datetime
from flask.ext.mail import Mail
from flask.ext.mail import Message
from flask.ext.sqlalchemy import Pagination
import re
import models


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
def create_article(title,content,title_image,article_session_id,is_draft,user_id,group_id,category_id,abstract,book_id,special_id=None):
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
		article.special_id=special_id
		db_session.commit()
		return result[0].article_id
	else:
		article=Article(title=title,content=content,picture=title_image,time=datetime.now(),user_id=user_id,article_session_id=article_session_id,is_draft=is_draft,groups=group_id,category=category_id,abstract=abstract,book_id=book_id,special_id=special_id)
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

def create_activity(title,content,title_image,activity_session_id,activity_time,abstract,place):
	result=db_session.query(Activity).filter_by(activity_session_id=activity_session_id).all()
	if len(result)>0:
		activity=db_session.query(Activity).filter_by(activity_session_id=activity_session_id).scalar()
		activity.name=title
		activity.content=content
		activity.picture=title_image
		activity.create_time=datetime.now()
		activity.activity_time=activity_time
		activity.abstract=abstract
		activity.place=place
		db_session.commit()
	else:
		activity=Activity(name=title,content=content,picture=title_image,create_time=datetime.now(),activity_session_id=activity_session_id,activity_time=activity_time,abstract=abstract,place=place)
		db_session.add(activity)
		db_session.commit()

def get_user_id(nick):
	user_id=db_session.query(User.user_id).filter_by(nick=nick).first()
	return user_id[0]


#返回1个元组，result[0][0]是Article类的数据库实例，result[0][1]是该Article实例所对应的User.nick,是字符串,result[0][2]是该Article实例所对应的Book实例
def get_article_information(article_id):
	result=db_session.query(Article,User,Book).join(User,Book).filter(Article.article_id==article_id).all()
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

def create_special_authorized():
	nick=None
	if 'user_id' in session:
		result = db_session.query(User).filter_by(user_id=int(session['user_id'])).all()[0]
		return result.role == 3
		## 专栏作家或者管理员
	else:
	    return False

def create_new_special(name, user_id, picture, introduction):
    special = Special(name = name, user_id = user_id,
                       picture = picture, introduction = introduction,
                       time = datetime.now())
    db_session.add(special)
    db_session.commit()
    return db_session.query(Special).filter_by(user_id = user_id, name = name).all()[0].special_id

def get_userid_from_session():
	nick=None
	if 'user_id' in session:
		result = db_session.query(User).filter_by(user_id=int(session['user_id'])).all()
		return result[0].user_id
	return 0

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
        
def get_special_collect_info(user_id, special_id):
    query = db_session.query(Collection_Special).filter_by(user_id = user_id, special_id = special_id).all()
    return len(query)
    
def get_author_collect_info(user_id, author_id):
    query = db_session.query(Collection_User).filter_by(user_id = user_id, another_user_id = author_id).all()
    return len(query)

def get_special_article(special_id, page_id, sort):
    if sort == "time":
#        print ddd
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
	
	
##################################  收藏/取消收藏 专栏  ####################################
def collection_special(user_id, special_id):
    query = db_session.query(Collection_Special).filter_by(user_id = user_id, special_id = special_id).all()
    if len(query) == 0:
        collect_spe = Collection_Special(user_id = user_id, 
                                         special_id = special_id,
                                         time = datetime.now())
        query = db_session.query(Special).filter_by(special_id = special_id).all()[0]
        query.favor += 1
        
        db_session.add(collect_spe)
        db_session.commit()
        
    else:
        raise Exception

def collection_special_cancel(user_id, special_id):
    query = db_session.query(Collection_Special).filter_by(user_id = user_id, special_id = special_id).all()
    if len(query) != 0:
        db_session.delete(query[0])
        query = db_session.query(Special).filter_by(special_id = special_id).all()[0]
        query.favor -= 1
        db_session.commit()
        
    else:
        raise Exception

        
##################################  收藏/取消收藏 专栏作家  ####################################
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


def collection_special_author_cancel(user_id, special_id):
    query = db_session.query(Special).filter_by(special_id = special_id).all()
    another_user_id = query[0].user_id
    if (user_id == another_user_id):
        return "self"
    query = db_session.query(Collection_User).filter_by(user_id = user_id, another_user_id = another_user_id).all()
    if len(query) == 1:
        db_session.delete(query[0])
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
	result=db_session.query(Collection_User).filter(and_(Collection_User.user_id==user_id,Collection_User.another_user_id==another_user_id)).all()
	if len(result)>0:
		pass
	else:
		collection=Collection_User(user_id=user_id,another_user_id=another_user_id,time=datetime.now())
		db_session.add(collection)
		db_session.commit()
		update_collection_num(user_id,another_user_id,True)


def delete_user_collection(another_user_id,user_id):
	db_session.query(Collection_User).filter(and_(Collection_User.user_id==user_id,Collection_User.another_user_id==another_user_id)).delete()
	db_session.commit()
	update_collection_num(user_id,another_user_id,False)

def update_collection_num(user_id,another_user_id,is_add):
	user=db_session.query(User).filter_by(user_id=user_id).scalar()
	another_user=db_session.query(User).filter_by(user_id=another_user_id).scalar()
	if is_add:
		user.follow_num+=1
		another_user.be_followed_num+=1
	else:
		user.follow_num-=1
		another_user.be_followed_num-=1		
	db_session.commit()

def get_hot_ground_acticle():
	result=db_session.query(Article,User.nick).join(User).filter(Article.groups=='1').order_by(desc(Article.coins)).limit(10).all()
	return result

def get_article_group_by_coin(groups,category):
	result=db_session.query(Article,User.nick).join(User).filter(and_(Article.groups==groups,Article.category==category)).order_by(desc(Article.coins)).limit(10).all()
	return result


def has_collected(user_id,another_user_id):
	result=db_session.query(Collection_User).filter(and_(Collection_User.user_id==user_id,Collection_User.another_user_id==another_user_id)).all()
	if len(result)>0:
		return 'yes'
	else:
		return 'no'


def create_message(to_user_id,user_id,content):
	message=models.Message(user_id=user_id,to_user_id=to_user_id,content=content,time=datetime.now())
	#message=models.Message(user_id,to_user_id,content,datetime.now())
	db_session.add(message)
	db_session.commit()

def user_coin_add(user_id,num):
	user=db_session.query(User).filter_by(user_id=user_id).scalar()
	user.coin+=num
	db_session.commit()
def user_coin_sub(user_id,num):
	user=db_session.query(User).filter_by(user_id=user_id).scalar()
	user.coin-=num
	db_session.commit()
def article_coin_add(article_id,num):
	article=db_session.query(Article).filter_by(article_id=article_id).scalar()
	article.coins+=num
	db_session.commit()
	article=db_session.query(Article).filter_by(article_id=article_id).first()
	user_coin_add(user_id=article.user_id,num=num)

def process_article_award(user_id,article_id,award_num):
	article=db_session.query(Article).filter_by(article_id=article_id).first()
	if article.user_id==user_id:
		return 'fail'
	else:
		user_coin_sub(user_id=user_id,num=award_num)
		article_coin_add(article_id=article_id,num=award_num)
		return 'success'

def examine_article_id(article_id):
	result=db_session.query(Article).filter_by(article_id=article_id).all()
	if len(result)>0:
		return True
	else:
		return False

def collection_article(user_id,article_id):
	article=db_session.query(Article).filter_by(article_id=article_id).first()
	result=db_session.query(Collection_Article).filter(and_(Collection_Article.user_id==user_id,Collection_Article.article_id==article_id)).all()
	if article.user_id==user_id:
		return 'fail'
	elif len(result)>0:
		return 'already'
	else:
		collection_article=Collection_Article(user_id=user_id,article_id=article_id,time=datetime.now())
		db_session.add(collection_article)
		db_session.commit()
		return 'success'

def collection_activity(user_id,activity_id):
	result=db_session.query(Collection_Activity).filter(and_(Collection_Activity.activity_id==activity_id,Collection_Activity.user_id==user_id)).all()
	if len(result)>0:
		return 'already'
	else:
		collection_activity=Collection_Activity(user_id=user_id,activity_id=activity_id,time=datetime.now())
		db_session.add(collection_activity)
		db_session.commit()
		return 'success'

def update_article_favor(article_id):
	article=db_session.query(Article).filter_by(article_id=article_id).scalar()
	article.favor+=1
	db_session.commit()

def update_activity_favor(activity_id):
	activity=db_session.query(Activity).filter_by(activity_id=activity_id).scalar()
	activity.favor+=1
	db_session.commit()


def get_current_activity_list(time):
	result=db_session.query(Activity).filter(Activity.activity_time>time).all()
	return result

def get_passed_activity_list(time):
	result=db_session.query(Activity).filter(Activity.activity_time<time).limit(4).all()
	return result

def get_follow_num(user_id):
	result=db_session.query(Collection_User).filter_by(user_id=user_id).all()
	return len(result)

def get_be_followed_num(user_id):
	result=db_session.query(Collection_User).filter_by(another_user_id=user_id).all()
	return len(result)


def get_article_pagination_by_user_id(user_id,by_time,page_id):
	if by_time:
		query=db_session.query(Article).filter(Article.user_id==user_id).order_by(desc(Article.time))
	else:
		query=db_session.query(Article).filter(Article.user_id==user_id).order_by(desc(Article.coins))
	return paginate(query,page_id,10,False)

def get_collection_author_list(user_id):
	result=db_session.query(User).join(Collection_User,Collection_User.another_user_id==User.user_id).filter(Collection_User.user_id==user_id).all()
	return result

def get_comment_pagination_by_user_id(user_id,page_id):
	query=db_session.query(Comment,Article).join(Article).filter(Comment.user_id==user_id).order_by(desc(Comment.time))
	return paginate(query,page_id,4,False)

def get_article_draft_pagination(user_id,page_id):
	query=db_session.query(Article).filter(and_(Article.user_id==user_id,Article.is_draft=='1'))
	return paginate(query,page_id,10,False)

def get_article_collection_pagination(user_id,page_id):
	query=db_session.query(Article).join(Collection_Article,Collection_Article.article_id==Article.article_id).filter(Collection_Article.user_id==user_id)
	return paginate(query,page_id,10,False)

def get_activity_collection_pagination(user_id,page_id):
	query=db_session.query(Activity).join(Collection_Activity,Collection_Activity.activity_id==Activity.activity_id).filter(Collection_Activity.user_id==user_id)
	return paginate(query,page_id,10,False)

def get_user_collection_pagination(user_id,page_id):
	query=db_session.query(User).join(Collection_User,Collection_User.another_user_id==User.user_id).filter(Collection_User.user_id==user_id)
	return paginate(query,page_id,10,False)

def get_special_collection_pagination(user_id,page_id):
	query=db_session.query(Special).join(Collection_Special,Collection_Special.special_id==Special.special_id).filter(Collection_Special.user_id==user_id)
	return paginate(query,page_id,10,False)

def get_fans_pagination(user_id,page_id):
	query=db_session.query(User).join(Collection_User,Collection_User.another_user_id==User.user_id).filter(Collection_User.user_id==user_id)
	return paginate(query,page_id,10,False)

##目前来说，3是管理员
def get_message_pagination(user_id,page_id):
	query=db_session.query(models.Message,User).join(User,User.user_id==models.Message.user_id).filter(and_(models.Message.to_user_id==user_id,models.Message.user_id!=3))
	return paginate(query,page_id,10,False)

def get_received_comment_pagination(user_id,page_id):
	query=db_session.query(Comment,User,Article).join(User,User.user_id==Comment.user_id).join(Article).filter(Comment.to_user_id==user_id)
	return paginate(query,page_id,10,False)
##目前来说，3是管理员
def get_notification_pagination(user_id,page_id):
	query=db_session.query(models.Message).filter(and_(models.Message.to_user_id==user_id,models.Message.user_id==3))
	return paginate(query,page_id,10,False)


def get_has_prev(pagination):
	if pagination.has_prev:
		return 'yes'
	else:
		return 'no'
def get_has_next(pagination):
	if pagination.has_next:
		return 'yes'
	else:
		return 'no'
