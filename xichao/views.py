# -*- coding: utf-8 -*-
'''

	视图模块

	定义路由
	定义并实现处理函数
	渲染视图
	
	文件结构：
	    主要URL：
    	    主页  /   /test
	        注册  /register   /upload/avatar  /upload/avatar/<filename>
	        登陆  /login
	        注销  /logout
	        忘记密码  /forgetPassword
	        重置密码  /resetPassword
	        邮箱验证    /verify
	        文章页面    /article/<int:article_id>
	        专栏页面    /special/<int:special_id>/page/<int:page_id>
	        专栏详情    /column_detail    /upload/special/<filename>
	        写文章
	            文章编辑页面       /article_upload
	            文章题图文件上传    /upload_article_title_image
	            获得文章题图       /upload/article/article_title_image/<filename>
	            UEditor交互       /editor/
	            获得文章中的图片    /editor_upload/<filename>
	            完成文章编辑       /article/finish
	            完成草稿编辑       /article/draft
	            
	    
	    辅助URL：
	        美图秀秀配置  /crossdomain.xml
	        图片剪裁器    /upload/tailor/title_image        /upload/tailor/avatar
	        
        Ajax请求：
            注册信息验证  /ajax_register

        已废弃：
            /article/test
            
'''
from xichao import app
from functions import *
from flask import redirect,url_for,render_template,request,flash,session,make_response,send_from_directory,jsonify,abort
from models import User
from database import db_session
from datetime import datetime
from forms import RegistrationForm,LoginForm,ForgetPasswordForm,ResetPasswordForm
from wtforms import Form
from werkzeug.datastructures import ImmutableMultiDict
from flask.ext.sqlalchemy import Pagination
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


##################################  美图秀秀配置文件  ##################################

#老版本无法打开localhost:5000，会404错误
#由于只需要crossdomain.xml，故单独路由
@app.route('/crossdomain.xml')
def xiuxiu_config():
	return send_from_directory(os.path.dirname(__file__),'crossdomain.xml')
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
	
	
####################################  注册  ##################################
##TODO：注册表单的头像链接要随着表单一起发送过来
@app.route('/register', methods=['GET', 'POST'])
def register():
	# print request.form
	form = RegistrationForm(request.form)
	if request.method == 'POST' and form.validate():
		user = User(nick=form.nick.data, email=form.email.data, role=1, register_time=datetime.now(), 
					last_login_time=datetime.now(), password=encrypt(form.password.data),state='0',photo=request.form['avatar'])
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


##################################  登陆  ##################################
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


##################################  忘记密码  ##################################
@app.route('/forgetPassword',methods=['GET', 'POST'])
def forgetPassword():
	error = None
	form = ForgetPasswordForm(request.form)

	if request.method == 'POST' and form.validate():
		nick = get_nick_by_email(form.email.data)
		password = get_password_by_email(form.email.data)
		send_resetpassword_email(nick, password, form.email.data) #待修改
		flash(u'我们已向你的注册邮箱发送了一份密码重置邮件')
		return redirect(url_for('test'))
	return render_template('forgetPassword.html', nick = None, form = form, error = error)
	
##################################  重置密码  ##################################
@app.route('/resetPassword/<nick>/<password>',methods=['GET', 'POST'])
def resetPassword(nick, password):
	if check_nickpassword_match(nick, password): #nick和password是否匹配
		form = ResetPasswordForm(request.form)
		if request.method == 'POST' and form.validate():
			update_password(nick, form.password.data) #重设密码
			session['user'] = nick #session增加用户
			flash(u'密码修改成功，正在跳转')
			return redirect(url_for('test'))
		else:
			return render_template('resetPassword.html', nick=None, form=form)
	else:
		return redirect(url_for('login'))


##################################  邮箱验证  ##################################
##TODO：邮箱验证成功的flash界面，验证失败的flash界面
@app.route('/verify')
def verify():
	nick=request.args.get('nick')
	password=request.args.get('secret')
	state=get_state(nick,password)
	if state:
		update_state(nick)
	return redirect(url_for('test'))
	
	
##################################  文章页面  ##################################
@app.route('/article/<int:article_id>',methods=['GET'])
def article(article_id):
	article=get_article_information(article_id)
	#comment初始显示5-6条，下拉显示全部
	comments=get_article_comments(article_id)
	update_read_num(article_id)
	return render_template('test_article.html',article=article[0],author=article[1],book=article[2],avatar=article[3],comments=comments,nick=getNick())

##################################  专栏页面  ##################################
@app.route('/special', methods=['GET'])
def special():
    try:
        special_id = int(request.args.get('id'))
        page_id = int(request.args.get('page'))
    except Exception:
        abort(404)
    
    special = get_special_information(special_id)
    if (special == None):
        abort(404)
    author = get_special_author(special.user_id)

	#article的分页对象，articles_pagination.items获得该分页对象中的所有内容，为一个list

    articles_pagination = get_special_article(special_id, page_id)
    return render_template('special_detail.html',
                            special_title = special.name,
                            special_author = author.nick,
                            special_author_slogon = author.slogon,
                            special_introduction = special.introduction,
                            special_image = special.picture,
                            special_author_avatar = author.photo,
                            articles_pagination = articles_pagination)
#                            articles_pagination = articles_pagination)


##################################  专栏详情页面  ##################################
#TODO 专栏详情尽量改成special detail
@app.route('/special_detail')
def coloum_detail():
	return render_template('special_detail.html', nick = getNick())


@app.route('/upload/special/<filename>')
def uploaded_special_image(filename):
	return send_from_directory(app.config['SPECIAL_DEST'],filename)


##################################  写文章  ##################################




##文章题图上传路径
@app.route('/upload_article_title_image', methods=['GET', 'POST'])
def save_title_image():
	title_image = request.files['upload_file']
	#设置默认题图
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
	abstract_abstract_with_img=request.form['abstract']
	abstract_plain_text=get_abstract_plain_text(abstract_abstract_with_img)
	if len(abstract_plain_text)<191:
		abstract=abstract_plain_text[0:len(abstract_plain_text)-1]+'......'
	else:
		abstract=abstract_plain_text[0:190]+'......'
	user_id=get_user_id(session['user'])
	create_article(title=title,content=content,title_image=title_image,user_id=user_id,article_session_id=session['article_session_id'],is_draft='1',group_id=group_id,category_id=category_id,abstract=abstract)
	return u'草稿保存成功'



'''

		ajax请求处理模块
		
		接收前端页面发送的json格式ajax请求
		根据请求参数，形成RegistrationForm类的实例
		调用RegistrationForm类的validate()方法，形成errors信息
		根据errors信息，形成json格式的ajax响应


'''

####################################  注册信息验证  ####################################

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


##################################	书籍 ##################################
#书籍图片的存储路径
@app.route('/book/picture/<filename>')
def uploaded_book_picture(filename):
	return send_from_directory(app.config['BOOK_PICTURE_DEST'],filename)



##################################	评论处理 ##################################
@app.route('/article/comment',methods=['POST'])
def comment():
	content=request.form['content']
	to_user_id=request.form['to_user_id']
	article_id=request.form['article_id']
	create_comment(content,to_user_id,article_id)
	update_comment_num(article_id)
	time=str(datetime.now()).rsplit('.',1)[0]
	return time


##################################	已废弃 ##################################

##################################	article_test ##################################
@app.route('/article/test')
def article_test():
	return render_template('test_article.html')
