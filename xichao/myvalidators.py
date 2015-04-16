# -*- coding: utf-8 -*-
'''
	
	定制验证器模块

	定义并实现了个人定制的验证器函数，被用于在表单验证过程中调用
'''
from wtforms import Form, BooleanField, TextField, PasswordField, validators, ValidationError
from functions import nick_exist,email_exist,cardID_exist

##################################  注册验证器  ####################################
def nick_validator(form,field):
	message=u'该昵称已存在'
	nick=field.data
	if nick_exist(nick):
		raise ValidationError(message)

def cardID_validator(form, field):
	message=u'该卡号已被绑定'
	cardID=field.data
	if cardID_exist(cardID):
		raise ValidationError(message)

def email_validator(form,field):
	message=u'该邮箱已注册'
	email=field.data
	if email_exist(email):
		raise ValidationError(message)

def email_exist_validator(form, field):
	message=u'邮箱不存在'
	email=field.data
	if not email_exist(email):
		raise ValidationError(message)