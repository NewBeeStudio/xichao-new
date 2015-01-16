# -*- coding: utf-8 -*-
from wtforms import Form, BooleanField, TextField, PasswordField, validators, ValidationError
from functions import nick_exist


def nick_validator():
	message=u'该昵称已存在'
	def _nick_validator(form, field):
		nick=field.data
		if nick_exist(nick):
			raise ValidationError(message)
	return _nick_validator
