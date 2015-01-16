# -*- coding: utf-8 -*-
'''

	视图模块

	定义路由
	定义并实现处理函数
	渲染视图

'''
from xichao import app
from functions import *
from flask import redirect,url_for,render_template,request,flash,session,make_response
from models import User
from database import db_session
from datetime import datetime
from forms import RegistrationForm,LoginForm
from wtforms import Form
from werkzeug.datastructures import ImmutableMultiDict
@app.route('/')
def default():
	return redirect(url_for('test'))


@app.route('/logout')
def logout():
	session.pop('username', None)
	flash('You were logged out')
    return redirect(url_for('index'))


@app.route('/test')
def test():
	nick=None
	if 'user' in session:
		nick=session['user']
	else if request.cookies.get('user')!=None:
		nick=request.cookies.get('user')
	return 'hello'


@app.route('/register', methods=['GET', 'POST'])
def register():
	#re=ImmutableMultiDict([('username', u'dddd'), ('password', u''), ('email', u'')])
	#form2 = RegistrationForm(re)
	form = RegistrationForm(request.form)
	if request.method == 'POST' and form.validate():
		user = User(form.nick.data, form.email.data, 1, datetime.now(), datetime.now(), encrypt(form.password.data))
		db_session.add(user)
		db_session.commit()
		session['user']=request.form['nick']
		flash(u'注册成功，正在跳转')
		return redirect(url_for('test'))
	#form2.validate()
	#print(form2.errors.get('email')[0])
	return render_template('register.html', form=form)

@app.route('/login',methods=['GET','POST'])
def login():
	error=None
	form=LoginForm(request.form)
	print type(form.stay.data)
	if request.method=='POST' and form.validate():
		email=form.email.data
		password=form.password.data
		nick=get_nick(email,password)
		if nick:
			session['user']=nick
			flash(u'登陆成功，正在跳转')
			response=make_response(redirect(url_for('test')))
			if form.stay.data:
				response.set_cookie('user',nick)
			return response
			#return redirect(url_for('test'))
		else:
			error=u'邮箱或密码错误'
	return render_template('login.html', form=form, error=error)