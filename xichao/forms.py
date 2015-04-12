# -*- coding: utf-8 -*-
'''
	表单模块

	定义了表单
	定义了验证器，验证器可以是内建验证器，也可以是定制验证器
'''
from wtforms import Form, BooleanField, TextField, PasswordField, validators, FileField, HiddenField
from myvalidators import *
from wtforms.csrf.session import SessionCSRF
from datetime import timedelta
from flask import request,session
from xichao import app



#注册表单
class RegistrationForm(Form):
	email = TextField(u'注册邮箱：', [validators.Required(u'邮箱必须'),validators.Email(message=u'邮箱不合法'),email_validator])
	nick = TextField(u'昵称：',[validators.Required(u'昵称必须'),validators.Length(min=2,max=10,message=u'昵称长度需在2-10之间'),nick_validator])
	password = PasswordField(u'密码：', [validators.Required(u'密码必须')])
	confirm = PasswordField(u'确认密码：', [validators.Required(u'确认密码必须'),validators.EqualTo('password', message=u'密码不匹配')])
	#avatar = HiddenField()
	#photo = FileField(u'上传头像')

#登录表单
class LoginForm(Form):
	email=TextField(u'邮箱',[validators.Required(u'邮箱必须')])
	password=PasswordField(u'密码',[validators.Required(u'密码必须')])
	stay=BooleanField(u'下次自动登录')

#忘记密码（只需要验证邮箱）
class ForgetPasswordForm(Form):
	email=TextField(u'邮箱：',[validators.Required(u'邮箱必须'), validators.Email(message=u'邮箱不合法'), email_exist_validator])

#重设密码（验证密码）
class ResetPasswordForm(Form):
	password = PasswordField(u'密码：', [validators.Required(u'密码必须')])
	confirm = PasswordField(u'确认密码：', [validators.Required(u'确认密码必须'),validators.EqualTo('password', message=u'密码不匹配')])

