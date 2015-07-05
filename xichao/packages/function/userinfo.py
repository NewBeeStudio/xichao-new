# -*- coding: utf-8 -*-
from imports import *

def get_user_id(nick):
	user_id=db_session.query(User.user_id).filter_by(nick=nick).first()
	return user_id[0]

###################################  昵称函数  ####################################
def getNick():
	nick=None
	if 'user_id' in session:
		result = db_session.query(User.nick).filter_by(user_id=int(session['user_id'])).first()
		nick = result[0]
	return nick

###################################  头像函数  ####################################
def get_avatar():
	nick=getNick()
	if nick == None:
		return None
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