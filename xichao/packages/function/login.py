# -*- coding: utf-8 -*-
from imports import *

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