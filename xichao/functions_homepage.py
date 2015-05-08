# -*- coding: utf-8 -*-

from xichao import app ## for app.config()
from database import db_session
from models import User

from sqlalchemy import  and_ ## seems to be useless
from flask import session

import os  ## for os.path


##################################  个人主页函数  ####################################


def update_user_basic_information_by_user_id(user_id,nick,gender,birthday,phone):
	user=db_session.query(User).filter_by(user_id=user_id).scalar()
	user.nick=nick
	user.gender=gender
	user.birthday=birthday
	user.phone=phone
	db_session.commit()
	##删除原先的头像
	if birthday==None and phone!=None:
		return 'success_no_birthday'
	elif birthday!=None and phone==None:
		return 'success_no_phone'
	elif birthday==None and phone==None:
		return 'success_no_birthday_phone'
	else:
		return 'success'

def delete(file_path):
	file_path_list=file_path.split('/')
	file_path_list_length=len(file_path_list)
	filename=file_path_list[file_path_list_length-1]
	if filename in app.config['DEFAULT_FILE']:
		pass
	else:
		try:
			os.remove(os.path.join(os.path.dirname(__file__),file_path[1:]))
			print 'delete file success'
		except Exception,e:
			print 'delete file fail'
			print e

def update_user_avatar(user_id,avatar):
	user=db_session.query(User).filter_by(user_id=user_id).scalar()
	old_avatar=user.photo
	user.photo=avatar
	db_session.commit()
	delete(old_avatar)
	return 'success'

def update_user_cover(user_id,cover):
	user=db_session.query(User).filter_by(user_id=user_id).scalar()
	old_cover=user.cover
	user.cover=cover
	db_session.commit()
	delete(old_cover)
	return 'success'

def update_user_slogon(user_id,slogon):
	user=db_session.query(User).filter_by(user_id=user_id).scalar()
	user.slogon=slogon
	db_session.commit()
	return 'success'

def update_member_id(user_id,member_id):
	user=db_session.query(User).filter_by(user_id=user_id).scalar()
	user.member_id=member_id
	try:
		db_session.commit()
		return 'success'
	except:
		return 'fail'