# -*- coding: utf-8 -*-
from wtforms import Form, BooleanField, TextField, PasswordField, validators
from myvalidators import *

#注册表单
class RegistrationForm(Form):
	email = TextField(u'注册邮箱：', [validators.Required(u'邮箱必须'),validators.Email(message=u'邮箱不合法')])
	nick = TextField(u'昵称：',[validators.Required(u'昵称必须'),nick_validator])
	password = PasswordField(u'密码：', [validators.Required(u'密码必须')])
	confirm = PasswordField(u'确认密码：', [validators.Required(u'确认密码必须'),validators.EqualTo('password', message=u'密码不匹配')])