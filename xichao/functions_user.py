# -*- coding: utf-8 -*-

from database import db_session
from models import User,Article,Activity,Comment_activity,\
Special,Comment,Collection_User,Collection_Special,Collection_Article,Collection_Activity
from xichao import app
from functions import update_comment_num


from sqlalchemy import  and_
from datetime import datetime
from hashlib import md5
from werkzeug import secure_filename
from flask import render_template,session
from flask.ext.mail import Mail
from flask.ext.mail import Message

##################################  注册函数  ####################################
def nick_exist(nick):
	result=db_session.query(User).filter_by(nick=nick).all()
	if len(result)>0:
		return True
	else:
		return False

def is_chinese(uchar):
    """判断一个unicode是否是汉字"""
    if uchar >= u'\u4e00' and uchar<=u'\u9fa5':
        return True
    else:
        return False

def nick_validate(nick):
	format="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_"
	for char in nick:
		if (not char in format) and (not is_chinese(char)):
			return False
	return True


def email_exist(email):
	result=db_session.query(User).filter_by(email=email).all()
	if len(result)>0:
		return True
	else:
		return False

def cardID_exist(cardID):
	result=db_session.query(User).filter_by(member_id = cardID).all()
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
    verify_url=app.config['HOST_NAME']+'/verify?nick='+nick+'&secret='+password
    mail=Mail(app)

    msg=Message(u'曦潮书店',sender=app.config['ADMINS'][0],recipients=[email])

    msg.body='text body'
    msg.html = render_template('test_verify_email.html',verify_url=verify_url,nick=nick)
    with app.app_context():
        try:
            mail.send(msg)
            return True
        except Exception,e:
            print "\n\n\n\n\n\n", "NoNoNoNoNoNoNo!", "\n\n\n\n\n\n"
            print str(e)
            return False

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

	msg=Message(u'重置曦潮网站密码',sender=app.config['ADMINS'][0],recipients=[email])

	msg.body='text body'
	msg.html = render_template('resetPasswordMail.html',nick=nick,verify_url=verify_url)
	with app.app_context():
		try:
			mail.send(msg)
			return True
		except:
			return False

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
        update_collection_num(user_id,another_user_id,True)
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
        update_collection_num(user_id,another_user_id,False)
    else:
        return "already"
    return "success"


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


###################################  评论函数  ####################################
def create_comment(content,to_user_id,article_id,reply_to_comment_id):
	user_id=int(session['user_id'])
	comment=Comment(article_id=article_id,content=content,user_id=user_id,to_user_id=to_user_id,time=datetime.now(),reply_to_comment_id=reply_to_comment_id)
	db_session.add(comment)
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


def create_message(to_user_id,user_id,content):
	message=models.Message(user_id=user_id,to_user_id=to_user_id,content=content,time=datetime.now())
	#message=models.Message(user_id,to_user_id,content,datetime.now())
	db_session.add(message)
	db_session.commit()

def create_notification(user_id,content):
	user_list=db_session.query(User).filter(User.role!=3).all();
	for user in user_list:
		create_message(user.user_id,user_id,content)


def user_coin_add(user_id,num):
	user=db_session.query(User).filter_by(user_id=user_id).scalar()
	user.coin+=num
	db_session.commit()
def user_coin_sub(user_id,num):
	user=db_session.query(User).filter_by(user_id=user_id).scalar()
	user.coin-=num
	db_session.commit()

#######################################  删除一条接收到的评论 start ########################################
def pretreamentment_received_comment_delete(received_comment_id):
	article=db_session.query(Article).join(Comment,Comment.article_id==Article.article_id).filter(Comment.comment_id==received_comment_id).first()
	update_comment_num(article.article_id,False)

def delete_received_comment_by_comment_id(received_comment_id,user_id):
	comment=db_session.query(Comment).filter_by(comment_id=received_comment_id).first()
	if comment.to_user_id!=user_id or comment==None:
		return 'fail'
	else:
		pretreamentment_received_comment_delete(received_comment_id)
		db_session.query(Comment).filter_by(comment_id=received_comment_id).delete()
		db_session.commit()
		return 'success'
#######################################  删除一条接收到的评论 end ########################################


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

#收藏了用户
def has_collected(user_id,another_user_id):
	result=db_session.query(Collection_User).filter(and_(Collection_User.user_id==user_id,Collection_User.another_user_id==another_user_id)).all()
	if len(result)>0:
		return 'yes'
	else:
		return 'no'
