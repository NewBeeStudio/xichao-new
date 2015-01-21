# -*- coding: utf-8 -*-
'''

	视图模块

	定义路由
	定义并实现处理函数
	渲染视图

'''
from xichao import app
from functions import *
from flask import redirect,url_for,render_template,request,flash,session,make_response,send_from_directory,jsonify
from models import User
from database import db_session
from datetime import datetime
from forms import RegistrationForm,LoginForm
from wtforms import Form
from werkzeug.datastructures import ImmutableMultiDict
import os


#PHOTO_DEST=os.path.join(os.path.dirname(__file__),'upload/avator')
HOST='http://127.0.0.1:5000'
ARTICLE_TITLE_DEST = os.path.join(os.path.dirname(__file__), 'upload/article/article_title')
ARTICLE_CONTENT_DEST = os.path.join(os.path.dirname(__file__), 'upload/article/article_content')
ARTICLE_DEST= os.path.join(os.path.dirname(__file__),'upload/article')

@app.route('/')
def default():
	return redirect(url_for('test'))

####################################  logout  ################################

@app.route('/logout')
def logout():
	session.pop('user', None)
	response=make_response(redirect(url_for('test')))
	if request.cookies.get('user')!=None:
		response.set_cookie('user','',expires=0)
	flash('你已退出')
	return response

####################################  test  ##################################

@app.route('/test')
def test():
	#print type(url_for('test'))
	nick=None
	if 'user' in session:
		nick=session['user']
	elif request.cookies.get('user')!=None:
		nick=request.cookies.get('user')
	return render_template('template.html', nick=nick,photo_url=app.config['HOST_NAME']+'/upload/avator/u24396247923879124612fm21gp02015011916361421656586.jpg')

####################################  register  ##################################

@app.route('/register', methods=['GET', 'POST'])
def register():
	#re=ImmutableMultiDict([('username', u'dddd'), ('password', u''), ('email', u'')])
	#form2 = RegistrationForm(re)
	#form = RegistrationForm(request.form)

	form = RegistrationForm(request.form)
	photo_error=None
	if request.method == 'POST' and form.validate():
		photo = request.files['photo']
		if photo:
			if allowed_file(photo.filename):
				photoname=get_secure_photoname(photo.filename)
				photo_url=os.path.join(app.config['PHOTO_DEST'], photoname)
				photo.save(photo_url)
			else:
				photo_error=u'文件名称不合法'
				return render_template('register.html', nick=None, form=form, photo_error=photo_error)
		user = User(form.nick.data, form.email.data, 1, datetime.now(), datetime.now(), encrypt(form.password.data),'0')
		db_session.add(user)
		db_session.commit()
		send_verify_email(form.nick.data,form.password.data,form.email.data)
		session['user']=request.form['nick']
		flash(u'注册成功，正在跳转')
		return redirect(url_for('test'))
	#form2.validate()
	#print(form2.errors.get('email')[0])
	return render_template('register.html', nick=None, form=form, photo_error=photo_error)

####################################  login  ##################################

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
	return render_template('login.html', nick=None, form=form, error=error)

####################################  email verify  ##################################

@app.route('/verify')
def verify():
	nick=request.args.get('nick')
	password=request.args.get('secret')
	state=get_state(nick,password)
	if state:
		update_state(nick)
	return redirect(url_for('test'))

####################################  article  ##################################

@app.route('/article/<int:article_id>',methods=['GET'])
def article(article_id):
	article=get_article_information(article_id)
	#comment初始显示5-6条，下拉显示全部
	comment=get_article_comment(article_id)
	return render_template('test_article.html',article=article,comment=comment)

####################################  special  ##################################

@app.route('/special/<int:special_id>/page/<int:page_id>',methods=['GET'])
def special(special_id,page_id=1):
	special=get_special_information(special_id)
	#article的分页对象，articles_pagination.items获得该分页对象中的所有内容，为一个list
	articles_pagination=get_special_article(special_id,page_id)
	return render_template('special.html',special=special,articles_pagination=articles_pagination)

####################################  get uploaded file  ##################################

@app.route('/upload/avator/<filename>')
def uploaded_file(filename):
	return send_from_directory(app.config['PHOTO_DEST'],filename)

	
#######################写文章#######################

@app.route('/upload/article/article_title_image/<filename>')
def uploaded_article_title_image(filename):
	return send_from_directory(app.config['ARTICLE_TITLE_DEST'],filename)

@app.route('/article_upload')
def article_upload():
    ## 只有登陆才能发表文章，需要增加判断
        ## 登陆的时候要在session中加入userid
    #session['userid'] = '1'
    ## 应该判断如果该用户草稿过多，则不能继续写文章
        ## TODO

    ## 插入一篇草稿
    #draft_id = new_draft()
    #session['draft_id'] = str(draft_id)
    
    ## 新建文章图片路径
    #os.makedirs(os.path.join(app.config['ARTICLE_TITLE_DEST'], session['draft_id']))
    #os.makedirs(os.path.join(app.config['ARTICLE_CONTENT_DEST'], session['draft_id']))

    #os.makedirs(os.path.join(ARTICLE_DEST,session['draft_id']))
    ## 前端应该在关闭页面前询问用户是否保留草稿
    ## 否则用户没打开一次界面都会产生一个草稿
    return render_template('test_article_upload.html')

	
@app.route('/editor/', methods=['GET', 'POST'])
def upload():
    from flask import json
    action = request.args.get('action')

    # 初始化，解析JSON格式的配置文件
    # 这里使用PHP版本自带的config.json文件
    if action == 'config':
        fp = open(os.path.join(app.static_folder, 'ueditor', 'php', 'config.json'))
        import re
        CONFIG = json.loads(re.sub(r'\/\*.*\*\/', '', fp.read()))
        # 初始化时，返回配置文件给客户端
        result = CONFIG
        return json.dumps(result)


    if action == 'uploadimage':
        result = {}
        upfile = request.files['upfile']  # 这个表单名称以配置文件为准
        # upfile 为 FileStorage 对象
        # 这里保存文件并返回相应的URL
        photoname = get_secure_photoname(upfile.filename)
        path = os.path.join(app.config['ARTICLE_CONTENT_DEST'], photoname)
        upfile.save(path)
        result = {
            "state": "SUCCESS",
            "url": "%s/editor_upload/%s" % (HOST, photoname),
            "title": "article1.jpg",
            "original": "article1.jpg"
        }
        return json.dumps(result)

@app.route('/editor_upload/<filename>')
def editor_upload(filename):
    from flask import send_from_directory
    return send_from_directory(app.config['ARTICLE_CONTENT_DEST'], filename)

@app.route('/article_finish',methods=['POST'])
def article_finish():
    content = request.form['content']
    title = request.form['title']
    title_image=request.form['title_image']
    print content
    print title

    ## TODO 用title和content更新数据库
    return title + "\n" + content
    ## 修改session['draft_id']对应的数据库项


@app.route('/article_draft',methods=['POST'])
def article_draft():
	content=request.form['content']
	title=request.form['title']
	title_image=request.form['title_image']
	return title + '\n'+content


'''

		ajax请求处理模块
		
		接收前端页面发送的json格式ajax请求
		根据请求参数，形成RegistrationForm类的实例
		调用RegistrationForm类的validate()方法，形成errors信息
		根据errors信息，形成json格式的ajax响应


'''
@app.route('/ajax_register', methods=['GET'])
def ajax_register_validate():
	email = request.args.get('email',0,type=unicode)
	nick = request.args.get('nick',0,type=unicode)
	password = request.args.get('password',0,type=unicode)
	confirm = request.args.get('confirm',0,type=unicode)

	request_form_from_ajax = ImmutableMultiDict([('email', email),('nick', nick), ('password', password), ('confirm', confirm)])
	form = RegistrationForm(request_form_from_ajax)
	form.validate()

	errors_return = {} #返回去的错误信息字典
	for param in ['email', 'nick', 'password', 'confirm']:
		if form.errors.get(param) == None:
			errors_return[param] = [u'']
		else:
			errors_return[param] = form.errors.get(param)

	return jsonify(email=errors_return.get('email')[0],nick=errors_return.get('nick')[0],password=errors_return.get('password')[0],confirm=errors_return.get('confirm')[0])


