# -*- coding: utf-8 -*-
from wtforms import Form, BooleanField, TextField, PasswordField, validators, ValidationError
from functions import nick_exist,email_exist


def nick_validator(form,field):
	message=u'该昵称已存在'
	nick=field.data
	if nick_exist(nick):
		raise ValidationError(message)


def email_validator(form,field):
	message=u'该邮箱已注册'
	email=field.data
	if email_exist(email):
		raise ValidationError(message)