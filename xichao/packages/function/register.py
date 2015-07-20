# -*- coding: utf-8 -*-
from imports import *

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

ALLOWED_EXTENSIONS=['jpg', 'png']
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
