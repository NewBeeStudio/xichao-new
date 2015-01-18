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
import os
from werkzeug import secure_filename
#from logging.handlers import SMTPHandler
from flask.ext.mail import Mail
from flask.ext.mail import Message

PHOTO_DEST=os.path.join(os.path.dirname(__file__),'upload')
HOST='http://127.0.0.1:5000'

@app.route('/')
def default():
	return redirect(url_for('test'))


@app.route('/logout')
def logout():
	session.pop('user', None)
	response=make_response(redirect(url_for('test')))
	if request.cookies.get('user')!=None:
		response.set_cookie('user','',expires=0)
	flash('你已退出')
	return response


@app.route('/test')
def test():
	print type(url_for('test'))
	nick=None
	if 'user' in session:
		nick=session['user']
	elif request.cookies.get('user')!=None:
		nick=request.cookies.get('user')
	return render_template('template.html', nick=nick)


@app.route('/register', methods=['GET', 'POST'])
def register():
	#re=ImmutableMultiDict([('username', u'dddd'), ('password', u''), ('email', u'')])
	#form2 = RegistrationForm(re)
	form = RegistrationForm(request.form)
	photo_error=None
	if request.method == 'POST' and form.validate():
		photo = request.files['photo']
		if photo:
			if allowed_file(photo.filename):
				filename=secure_filename(photo.filename)
				photoname=filename.rsplit('.',1)[0]+datetime.now().strftime('%Y%m%d%H%M%s')+'.'+filename.rsplit('.',1)[1]
				photo_url=os.path.join(PHOTO_DEST, photoname)
				photo.save(photo_url)
			else:
				photo_error=u'文件名称不合法'
				return render_template('test_register.html', form=form, photo_error=photo_error)
		user = User(form.nick.data, form.email.data, 1, datetime.now(), datetime.now(), encrypt(form.password.data),'0')
		db_session.add(user)
		db_session.commit()
		verify_url=HOST+url_for('verify')+'?nick='+form.nick.data+'&secret='+encrypt(form.password.data)
		mail=Mail(app)
		msg=Message(u'曦潮书店',sender='xichao_test@163.com',recipients=[form.email.data])
		msg.body='text body'
		msg.html = render_template('test_verify_email.html',verify_url=verify_url)
		with app.app_context():
			mail.send(msg)
		session['user']=request.form['nick']
		flash(u'注册成功，正在跳转')
		return redirect(url_for('test'))
	#form2.validate()
	#print(form2.errors.get('email')[0])
	return render_template('test_register.html', form=form, photo_error=photo_error)

@app.route('/login',methods=['GET','POST'])
def login():
	error=None
	form=LoginForm(request.form)
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
		else:
			error=u'邮箱或密码错误'
	return render_template('test_login.html', form=form, error=error)

@app.route('/verify')
def verify():
	nick=request.args.get('nick')
	password=request.args.get('secret')
	state=get_state(nick,password)
	if state:
		update_state(nick)
	return redirect(url_for('test'))