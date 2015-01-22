# -*- coding: utf-8 -*-
'''

	视图模块

	定义路由
	定义并实现处理函数
	渲染视图

'''
from xichao import app
from functions import *
from flask import redirect,url_for,render_template,request,flash,session,make_response,send_from_directory,jsonify,abort
from models import User
from database import db_session
from datetime import datetime
from forms import RegistrationForm,LoginForm
from wtforms import Form
from werkzeug.datastructures import ImmutableMultiDict
import os


GROUP=[u'广场',u'文章',u'专栏']
CATEGORY=[u'书评',u'影评',u'杂文',u'专栏文章']
#######################################  图片裁剪器  #########################################
##TODO：通过传参，缩为一个
@app.route('/upload/tailor/title_image')
def upload_title_image():
	return render_template('upload_title_image_tailor.html')


@app.route('/upload/tailor/avatar')
def upload_avatar():
	return render_template('upload_avatar_tailor.html')

#######################################  美图秀秀配置文件  #########################################
@app.route('/<filename>')
def xiuxiu_config(filename):
	if filename=='crossdomain.xml':
		return send_from_directory(os.path.dirname(__file__),filename)
	else:
		abort(404)


#######################################  注销  #########################################

@app.route('/logout')
def logout():
	#弹出session
	session.pop('user', None)
	response=make_response(redirect(url_for('test')))
	#删除cookie
	if request.cookies.get('user')!=None:
		response.set_cookie('user','',expires=datetime.now())
	flash('你已退出')
	return response

####################################  test  ##################################

@app.route('/test')
def test():
	nick=None
	#先从session中获取，若session中没有，再从cookie中获取，若都没有，则为默认值None
	if 'user' in session:
		nick=session['user']
	elif request.cookies.get('user')!=None:
		nick=request.cookies.get('user')
	return render_template('template.html', nick=nick)

####################################  register  ##################################
##TODO：注册表单的头像链接要随着表单一起发送过来
@app.route('/register', methods=['GET', 'POST'])
def register():
	print request.form
	form = RegistrationForm(request.form)
	if request.method == 'POST' and form.validate():
		user = User(form.nick.data, form.email.data, 1, datetime.now(), datetime.now(), encrypt(form.password.data),'0',request.form['avatar'])
		db_session.add(user)
		db_session.commit()
		send_verify_email(form.nick.data,form.password.data,form.email.data)
		session['user']=request.form['nick']
		flash(u'注册成功，正在跳转')
		return redirect(url_for('test'))
	return render_template('register.html', nick=None, form=form)

#接收上传的头像文件，保存并返回路径
@app.route('/upload/avatar',methods=['GET', 'POST'])
def save_avatar():
	avatar = request.files['avatar']
	avatar_name='default.jpg'
	if avatar:
		if allowed_file(avatar.filename):
			avatar_name=get_secure_photoname(avatar.filename)
			avatar_url=os.path.join(app.config['PHOTO_DEST'],avatar_name)
			avatar.save(avatar_url)
	return app.config['HOST_NAME']+'/upload/avatar/'+avatar_name

#为上传的头像文件提供服务
@app.route('/upload/avatar/<filename>')
def uploaded_avatar(filename):
	return send_from_directory(app.config['PHOTO_DEST'],filename)


####################################  login  ##################################
##TODO：cookie的过期时间
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
##TODO：邮箱验证成功的flash界面，验证失败的flash界面
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



	
#######################写文章#######################
##文章题图上传路径
@app.route('/upload_article_title_image', methods=['GET', 'POST'])
def save_title_image():
	title_image = request.files['upload_file']
	title_image_name = 'article_upload_pic_4.png'
	if title_image:
		if allowed_file(title_image.filename):
			title_image_name=get_secure_photoname(title_image.filename)
			title_image_url=os.path.join(app.config['ARTICLE_TITLE_DEST'], title_image_name)
			title_image.save(title_image_url)
	return app.config['HOST_NAME']+'/upload/article/article_title_image/'+title_image_name

#获得文章题图
@app.route('/upload/article/article_title_image/<filename>')
def uploaded_article_title_image(filename):
	return send_from_directory(app.config['ARTICLE_TITLE_DEST'],filename)

#写文章页面显示
@app.route('/article_upload/group/<int:group_id>/category/<int:category_id>')
def article_upload(group_id=3,category_id=4):
	#未登录用户跳转到登录页面，已登录用户，跳转到发表文章页面
	#判断请求链接是否合法
	if group_id in [1,2,3] and category_id in [1,2,3,4]:
		if category_id==4 and group_id!=3:
			abort(404)
		elif category_id<4 and group_id==3:
			abort(404)
		else:
			#判断用户是否登录
			if not 'user' in session:
				return redirect(url_for('login'))
			else:
				group=GROUP[group_id-1]
				category=CATEGORY[category_id-1]
				article_session_id=get_article_session_id()
				session['article_session_id']=str(article_session_id)
				os.makedirs(os.path.join(app.config['ARTICLE_CONTENT_DEST'], str(article_session_id)))
				upload_url='/group/'+str(group_id)+'/category/'+str(category_id)
				return render_template('test_article_upload.html',nick=session['user'],group=group,category=category,upload_url=upload_url)
	else:
		abort(404)


	'''
	if not 'user' in session:
		return redirect(url_for('login'))
	else:
		article_session_id=get_article_session_id()
		#将article_session_id放入session中，以访问该article_session_id下的文件夹下的文章内容图该值需要能够被写入文章的数据库表中
		session['article_session_id']=str(article_session_id)
		os.makedirs(os.path.join(app.config['ARTICLE_CONTENT_DEST'], str(article_session_id)))
		return render_template('test_article_upload.html',nick=session['user'],group=group,category=category)
	'''
#UEditor配置
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
        path = os.path.join(app.config['ARTICLE_CONTENT_DEST'], session['article_session_id'] ,photoname)
        upfile.save(path)
        result = {
            "state": "SUCCESS",
            "url": "%s/editor_upload/%s" % (app.config['HOST_NAME'], photoname),
            "title": "article1.jpg",
            "original": "article1.jpg"
        }
        return json.dumps(result)

#获得UEditor内的图片
@app.route('/editor_upload/<filename>')
def editor_upload(filename):
    return send_from_directory(os.path.join(app.config['ARTICLE_CONTENT_DEST'],session['article_session_id']), filename)

#文章完成时的提交路径
##TODO:可能是存在数据库中的草稿提交过来的，这时候只需要把is_draft字段更改就行
@app.route('/article/finish/group/<group_id>/category/<category_id>',methods=['POST'])
def article_finish(group_id,category_id):
    content = request.form['content']
    title = request.form['title']
    ##TODO 文章标题的安全性过滤
    title_image=request.form['title_image']
    user_id=get_user_id(session['user'])

    create_article(title=title,content=content,title_image=title_image,user_id=user_id,article_session_id=session['article_session_id'],is_draft='0',group_id=group_id,category_id=category_id)
    return u'文章保存成功'

#文章草稿的提交路径
@app.route('/article/draft/group/<group_id>/category/<category_id>',methods=['POST'])
def article_draft(group_id,category_id):
	content=request.form['content']
	title=request.form['title']
	title_image=request.form['title_image']
	user_id=get_user_id(session['user'])

	create_article(title=title,content=content,title_image=title_image,user_id=user_id,article_session_id=session['article_session_id'],is_draft='1',group_id=group_id,category_id=category_id)
	return u'草稿保存成功'




#专栏详情页面
@app.route('/column_detail')
def coloum_detail():
	return render_template('column_detail.html', nick = getNick())

@app.route('/upload/special/<filename>')
def uploaded_column_image(filename):
	return send_from_directory(app.config['SPECIAL_DEST'],filename)

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


