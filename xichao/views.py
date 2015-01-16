# -*- coding: utf-8 -*-
from xichao import app
from functions import *
from flask import redirect,url_for,render_template,request
from models import User
from database import db_session
from datetime import datetime
from forms import RegistrationForm
from wtforms import Form
from werkzeug.datastructures import ImmutableMultiDict
@app.route('/')
def default():
    return redirect(url_for('test'))

'''
@app.route('/index')
def index():
	username=None
	if session:
		username=session['username']
    return render_template('index.html',username=username)


@app.route('/register',methods=['GET','POST'])
def register():
	error = None
	if request.method=='POST':
		if user_exist(request.form['username']):
			error('invalid user')
		else:
			if create_user(request.form['username'],request.form['password']):
				flash('register success!')
				session['username']=request.form['username']
				redirect(url_for('index'))
	return render_template('register.html',error=error)
'''

'''
@app.route('/login',methods=['GET','POST'])
def login():
	error = None
	
	if request.method=='POST':
		if user_exit(request.form['username']):
			if encrypt(request.form['password'])!= get_user_encrypt_password(request.form['username']):
				error='invalid password'
			else:
				flash('login success!')
				session['username'] = request.form['username']
				redirect(url_for('index'))
		else:
			error('invalid user')
	
	return render_template('login.html',error=error)
'''

'''
@app.route('/logout')
def logout():
	session.pop('username', None)
	flash('You were logged out')
    return redirect(url_for('index'))
'''

@app.route('/test')
def test():
	return 'hello world'



@app.route('/register',methods=['GET','POST'])
def register():
	error=None
	username='admin'
	if nick_exist(username):
		error='invalid user'
		return error
	else:
		user=User(username,'754ss4d4@qq.com',1,datetime.now(),datetime.now(),encrypt('world'))
		db_session.add(user)
		db_session.commit()
		return 'yes'

@app.route('/reg', methods=['GET', 'POST'])
def reg():
    re=ImmutableMultiDict([('username', u'dddd'), ('password', u''), ('email', u'')])
    form = RegistrationForm(request.form)
    #print(request.form)
    form2 = RegistrationForm(re)
    if request.method == 'POST' and form.validate():
    	'''
        user = User(form.username.data, form.email.data,
                    form.password.data)
        db_session.add(user)
        flash('Thanks for registering')
        return redirect(url_for('login'))
        '''
        return 'yes'
    form2.validate()
    print(form2.errors.get('email')[0])
    #errors_dic={'username': form2.errors.get('username')[0]}
    return render_template('register.html', form=form)

