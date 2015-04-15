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
	        文章首页    /article
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
	        广场页   /square

	        活动页   /activity


	    辅助URL：
	        美图秀秀配置  /crossdomain.xml
	        图片剪裁器    /upload/tailor/title_image        /upload/tailor/avatar

        Ajax请求：
            注册信息验证  /ajax_register
	        收藏用户    /collection_user

        已废弃：
            /article/test

'''
from xichao import app, login_manager, login_serializer
from functions import *
from flask import redirect,url_for,render_template,request,flash,session,make_response,send_from_directory,jsonify,abort,json
from models import User
from database import db_session
from datetime import datetime,date
from forms import RegistrationForm,LoginForm,ForgetPasswordForm,ResetPasswordForm
from wtforms import Form
from werkzeug.datastructures import ImmutableMultiDict
from flask.ext.sqlalchemy import Pagination
import os

from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required
from itsdangerous import constant_time_compare, BadData
from hashlib import md5
from captcha import get_captcha
import time

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

@app.route('/upload/tailor/activity/title_image')
def upload_activity_title_image():
	return render_template('upload_activity_title_image_tailor.html')


##################################  美图秀秀配置文件  ##################################

#老版本无法打开localhost:5000，会404错误
#由于只需要crossdomain.xml，故单独路由
@app.route('/crossdomain.xml')
def xiuxiu_config():
	return send_from_directory(os.path.dirname(__file__),'crossdomain.xml')
#######################################  注销  #########################################

@app.route('/logout')
@login_required
def logout():
	#弹出sessio
	# session.pop('user', None)
	logout_user()
	response=make_response(redirect(url_for('index')))
	#删除cookie，flask-login已完成相应操作
	#if request.cookies.get('user')!=None:
	#	response.set_cookie('user','',expires=datetime.now())
	flash('你已退出')
	return response
####################################  index  ##################################
@app.route('/')
def default():
	return redirect(url_for('index'))

@app.route('/index')
def index():
    homepage_special_list, slideUrl = get_homepage_specials()
    most_hot_ground_article=get_most_hot_ground_article()
    most_hot_activity=get_most_hot_activity(datetime.now())
    hot_articles = get_hot_articles(10)
    return render_template('template.html', special_list = homepage_special_list,
                                            hot_articles = hot_articles,
                                            articles = get_special_article,
                                            slideUrl = slideUrl,
                                            get_author = get_nick_by_userid,
                                            most_hot_ground_article=most_hot_ground_article,
                                            most_hot_activity=most_hot_activity)
## 修改首页
@app.route('/modify_homepage')
@login_required
def modify_homepage():
    if (not create_special_authorized()):
        abort(404)
    allSpecial = get_all_special()
    return render_template('modify_homepage.html', allSpecial = allSpecial)

## 完成首页修改
@app.route('/modify_homepage_finish', methods=['GET'])
@login_required
def modify_homepage_finish():
    if (not create_special_authorized()):
        abort(404)
    special1 = request.args.get('special1')
    special2 = request.args.get('special2')
    special3 = request.args.get('special3')
    special4 = request.args.get('special4')

    url1 = request.args.get('url1')
    url2 = request.args.get('url2')
    url3 = request.args.get('url3')
    url4 = request.args.get('url4')

    return modify_homepage_func(special1, url1,
                                special2, url2,
                                special3, url3,
                                special4, url4)

## 上传首页所需图片
@app.route('/upload_homepage_image', methods=['POST'])
@login_required
def upload_homepage_image():
    for i in range(1,5):
        try:
            image = request.files['slide-image'+str(i)]

            if allowed_file(image.filename):
                image_name = get_secure_photoname(image.filename)
                image_url=os.path.join(app.config['HOMEPAGE_DEST'], image_name)
                image.save(image_url)



            return '/upload/homepage/'+image_name
        except Exception:
            pass
    return "failed"

## 获取首页图片
@app.route('/upload/homepage/<filename>')
def uploaded_homepage_image(filename):
	return send_from_directory(app.config['HOMEPAGE_DEST'],filename)

####################################  注册  ##################################
##TODO：注册表单的头像链接要随着表单一起发送过来
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    captcha, cap_code = get_captcha()
    if request.method == 'POST' and form.validate():
        user = User(nick=form.nick.data, email=form.email.data, role=1, register_time=datetime.now(), last_login_time=datetime.now(), password=encrypt(form.password.data),state='0',photo=request.form['avatar'],slogon='暂未填写')
        db_session.add(user)
        db_session.commit()
        #需要增加异常处理，捕获异常，
        send_verify_email(form.nick.data,encrypt(form.password.data),form.email.data)
        # session['user']=request.form['nick']
        user=User.query.filter_by(email=form.email.data).first()
        login_user(user)
        flash(u'注册成功，正在跳转')
        time.sleep(3)
        return redirect(url_for('index'))
	return render_template('register.html', form=form, captcha=captcha, cap_code=cap_code)

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
	return '/upload/avatar/'+avatar_name

#为上传的头像文件提供服务
@app.route('/upload/avatar/<filename>')
def uploaded_avatar(filename):
	return send_from_directory(app.config['PHOTO_DEST'],filename)


##############################cookie session相关#######################################
@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

#cookie token加密
@login_manager.token_loader
def load_token(token):
    try:
        max_age = app.config['REMEMBER_COOKIE_DURATION'].total_seconds()
        user_id, hash_a = login_serializer.loads(token, max_age=max_age)
    except BadData:
        return None
    user = User.query.get(user_id)
    if user is not None:
        hash_a = hash_a.encode('utf-8')
        hash_b = md5(user.password).hexdigest()
        if constant_time_compare(hash_a, hash_b):
            return user
    return None

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
			# session['user']=nick
			user=User.query.filter_by(email=form.email.data).first()
			login_user(user, remember=form.stay.data) #参数2：是否保存cookie
			flash(u'登陆成功，正在跳转')
			response=make_response(redirect(request.form.get("request_url") or url_for("index")))
			#if form.stay.data:
			#	response.set_cookie('user',nick)
			return response
		else:
			error=u'邮箱或密码错误'
	return render_template('login.html', request_url=request.form.get("request_url"), form=form, error=error)


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
		return redirect(url_for('index'))
	return render_template('forgetPassword.html', form = form, error = error)

##################################  重置密码  ##################################
@app.route('/resetPassword/<nick>/<password>',methods=['GET', 'POST'])
def resetPassword(nick, password):
	if check_nickpassword_match(nick, password): #nick和password是否匹配
		form = ResetPasswordForm(request.form)
		if request.method == 'POST' and form.validate():
			update_password(nick, form.password.data) #重设密码
			# session['user'] = nick #session增加用户
			user=User.query.filter_by(nick=nick).first()
			login_user(user)
			flash(u'密码修改成功，正在跳转')
			return redirect(url_for('index'))
		else:
			return render_template('resetPassword.html', form=form)
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
	return redirect(url_for('index'))


##################################  文章首页  ##################################
@app.route('/article/',methods=['GET', 'POST'])
@login_required
def article_main():
	##参数1=2表示文章
	book_review_list=get_article_group_by_coin('2','1')
	film_review_list=get_article_group_by_coin('2','2')
	essay_list=get_article_group_by_coin('2','3')
	return render_template('article.html',type=2,book_review_list=book_review_list,film_review_list=film_review_list,essay_list=essay_list)


##################################  文章页面  ##################################
@app.route('/article/<int:article_id>',methods=['GET'])
@login_required
def article(article_id):
	article=get_article_information(article_id)
	if article!=None:
		if article[0].is_draft=='1' and article[1].user_id!=current_user.user_id:
			abort(404)
		else:
			#comment初始显示5-6条，下拉显示全部
			session['article_session_id']=article[0].article_session_id
			comments=get_article_comments(article_id)
			if article[0].user_id==current_user.user_id:
				pass
			else:
				update_read_num(article_id)
			return render_template('test_article.html',article=article[0],author=article[1],book=article[2],avatar=get_avatar(),comments=comments,nick=getNick())
	else:
		abort(404)

##################################  专栏页面  ##################################
# 专栏列表页
@app.route('/special_all', methods=['GET'])
def special_all():
    try:
        view = request.args.get('view')
        sort = request.args.get('sort')
        page_id = int(request.args.get('page'))
    except Exception:
        abort(404)

    if sort != 'favor':
        sort = 'time'
        sort_change_url = '/special_all?view=%s&sort=favor&page=1'%(view)
    else:
        sort_change_url = '/special_all?view=%s&sort=time&page=1'%(view)

    if view != 'list':
        vieww = 'all'
        view_change_url = '/special_all?view=list&sort=%s&page=1'%(sort)
    else:
        view_change_url = '/special_all?view=all&sort=%s&page=1'%(sort)


    if view == 'list':  # list view
        specials_pagination = get_all_specials(sort, page_id, 5)
        return render_template('special_all_listView.html', sort = sort, view=view,
                                                  specials_pagination_list = specials_pagination,
                                                  author = get_special_author,
                                                  articles = get_special_article,
                                                  sort_change_url = sort_change_url,
                                                  view_change_url = view_change_url)
    else:   # all view
        specials_pagination = get_all_specials(sort, page_id, 15)
        return render_template('special_all_allView.html', sort = sort, view=view,
                                                  specials_pagination_all = specials_pagination,
                                                  author = get_special_author,
                                                  articles = get_special_article,
                                                  sort_change_url = sort_change_url,
                                                  view_change_url = view_change_url)


#专栏列表搜索
@app.route('/special_search', methods=['GET'])
def special_search():
    try:
        search = request.args.get('search')
        if search == '': abort(404)
    except Exception:
        abort(404)

    specials_pagination = get_search_specials(search)
    return render_template('special_search.html', specials_pagination = specials_pagination,
                                                  author = get_special_author,
                                                  articles = get_special_article)

# 专栏详情页
@app.route('/special', methods=['GET'])
def special():
    #URL样式：http://127.0.0.1:5000/special?id=2&page=1&sort=time
    try:
        special_id = int(request.args.get('id'))
        page_id = int(request.args.get('page'))
        sort = request.args.get('sort')
    except Exception:
        abort(404)

    #只有favor和time两种排序方式
    if (sort != 'favor'):
        sort = 'time'
        sort_change_url = "/special?id=%d&page=1&sort=favor" % (special_id)
    else:
        sort_change_url = "/special?id=%d&page=1&sort=time" % (special_id)

    special = get_special_information(special_id)
    if (special == None):
        abort(404)
    author = get_special_author(special.user_id)

#    print ddd
	#article的分页对象，articles_pagination.items获得该分页对象中的所有内容，为一个list
    login_user = get_userid_from_session()

    articles_pagination = get_special_article(special_id, page_id, sort, 5)
    author_other_article = get_special_author_other(special.user_id, special_id, 6)
#    print aaa
    related_other_special = get_related_special(special.user_id)
#    print aaa
    return render_template('special_detail.html',
                            author_itself = (special.user_id == login_user),
                            has_collected_special = get_special_collect_info(login_user, special_id),
                            has_collected_author = get_author_collect_info(login_user, special.user_id),
                            sort_change_url = sort_change_url,
                            special_id = special_id,
                            sort = sort,
                            other = author_other_article,
                            special_favor = special.favor,
                            special_title = special.name,
                            special_author = author.nick,
                            special_author_slogon = author.slogon,
                            special_introduction = special.introduction,
                            special_style = special.style,
                            special_total_issue = special.total_issue,
                            special_update_frequency = special.update_frequency,
                            special_coin = special.coin,
                            special_image = special.picture,
                            special_author_avatar = author.photo,
                            articles_pagination = articles_pagination,
                            related_other_special = related_other_special,
                            get_nick_by_userid = get_nick_by_userid)
#                            articles_pagination = articles_pagination)


## 创建专栏界面
@app.route('/create_special')
@login_required
def create_special():
    if (not create_special_authorized()):
        abort(404)
    return render_template('create_special.html')


## 修改专栏界面
@app.route('/modify_special')
@login_required
def modify_special():
    if (not create_special_authorized()):
        abort(404)
    return render_template('modify_special.html')

## 上传专栏题图文件
@app.route('/upload_special_title_image', methods=['GET', 'POST'])
def save_special_title_image():
	title_image = request.files['upload_file']
	#设置默认题图
	title_image_name = 'special_upload_pic.jpg'
	if title_image:
		if allowed_file(title_image.filename):
			title_image_name=get_secure_photoname(title_image.filename)
			title_image_url=os.path.join(app.config['SPECIAL_DEST'], title_image_name)
			title_image.save(title_image_url)
	return app.config['HOST_NAME']+'/upload/special/'+title_image_name

# 调用美图秀秀
@app.route('/upload/tailor/special_title_image')
def upload_special_title_image():
	return render_template('upload_special_title_image_tailor.html')


## 完成创建专栏的上传
@app.route('/create_special_finish', methods=['GET'])
@login_required
def create_special_finish():
    if (not create_special_authorized()):
        abort(404)

    try:
        title = request.args.get('title')
        content = request.args.get('content')
        title_image = request.args.get('title_image')

        style = request.args.get('style')
        total_issue = request.args.get('total_issue')
        update_frequency = request.args.get('update_frequency')
    except Exception:
        return "failed"

    try:
        author = request.args.get('author')
        author = get_userid_by_nick(author)
        if (len(author) == 0):
            return "nick_error"
    except Exception:
        return "failed"

    special_id = create_new_special(name = title,
                       user_id = author[0][0],
                       picture = title_image,
                       introduction = content,
                       style = style,
                       total_issue = total_issue,
                       update_frequency = update_frequency)

#    print "\n\n\n\n\n\n\n\nHERE  %d\n\n\n\n\n\n\n\n" % (special_id)
    return str(special_id)

## 完成修改专栏
@app.route('/modify_special_finish', methods=['GET'])
@login_required
def modify_special_finish():
    if (not create_special_authorized()):
        abort(404)

    try:
        title = request.args.get('title')
        content = request.args.get('content')
        title_image = request.args.get('title_image')

        style = request.args.get('style')
        total_issue = request.args.get('total_issue')
        update_frequency = request.args.get('update_frequency')
    except Exception:
        return "failed"

    try:
        author = request.args.get('author')
        author = get_userid_by_nick(author)
        if (len(author) == 0):
            return "nick_error"
    except Exception:
        return "failed"

    try:
        special_id = modify_special_func(name = title,
                                         user_id = author[0][0],
                                         picture = title_image,
                                         introduction = content,
                                         style = style,
                                         total_issue = total_issue,
                                         update_frequency = update_frequency)
        return str(special_id)
    except Exception:
        return "failed"

## 编辑专栏文章
@app.route('/special_article_upload', methods=['GET'])
@login_required
def special_article_upload():
    try:
        special_id = int(request.args.get('id'))
    except Exception:
        abort(404)

    author = get_special_information(special_id).user_id
    login_user = get_userid_from_session()
    if (author != login_user):
        abort(404)

    article_session_id = get_article_session_id()
    session['special_article_session_id'] = str(article_session_id)
    session['special_id'] = str(special_id)
    os.makedirs(os.path.join(app.config['ARTICLE_CONTENT_DEST'], str(article_session_id)))

    return render_template('special_article_upload.html')

# 修改专栏文章
@app.route('/special_article_modify/article/<int:article_id>')
def special_article_modify(article_id):
    article = get_article_information(article_id)

    try:
        special_id = int(article[0].special_id)
    except Exception:
        abort(404)

    author = article[0].user_id
    login_user = get_userid_from_session()
    if (author != login_user):
        abort(404)

    session['special_id'] = str(article[0].special_id)
    session['special_article_session_id'] = str(article[0].article_session_id)
    return render_template('special_article_modify.html',article=article[0],book=article[2])


# 删除专栏文章
@app.route('/special_article_remove', methods=['GET'])
def special_article_remove():
    try:
        article_id = request.args.get('id')
    except Exception:
        return "failed"

    user_id = get_userid_from_session()
    if delete_article_by_article_id(article_id, user_id) == 'fail':
        return "failed"
    return "success"


## 上传专栏文章
##TODO:可能是存在数据库中的草稿提交过来的，这时候只需要把is_draft字段更改就行
@app.route('/special_article_finish', methods=['POST'])
def special_article_finish():
    content = request.form['content']
    title = request.form['title']
    ##TODO 文章标题的安全性过滤
    title_image=request.form['title_image']
    abstract_abstract_with_img=request.form['abstract']
    book_picture=request.form['book_picture']
    book_author=request.form['book_author']
    book_press=request.form['book_press']
    book_page_num=request.form['book_page_num']
    book_price=request.form['book_price']
    book_press_time=request.form['book_press_time']
    book_title=request.form['book_title']
    book_ISBN=request.form['book_ISBN']
    book_binding=request.form['book_binding']


    abstract_plain_text=get_abstract_plain_text(abstract_abstract_with_img)
    if len(abstract_plain_text)<191:
        abstract=abstract_plain_text[0:len(abstract_plain_text)-1]+'......'
    else:
        abstract=abstract_plain_text[0:190]+'......'
    user_id = int(session['user_id'])
    book_id = create_book(book_picture = book_picture,
                                  book_author = book_author,
                                  book_press = book_press,
                                  book_page_num = book_page_num,
                                  book_price = book_price,
                                  book_press_time = book_press_time,
                                  book_title = book_title,
                                  book_ISBN = book_ISBN,
                                  book_binding = book_binding)
    article_id=create_article(title = title, content = content,
                              title_image = title_image, user_id = user_id,
                              article_session_id = session['special_article_session_id'],
                              is_draft ='0', special_id = int(session['special_id']),
                              group_id = '3', category_id = '0',
                              abstract = abstract,
                              book_id = book_id)
    update_article_num_for_special(int(session['special_id']),True)
    session.pop('special_id', None)
    session.pop('special_article_session_id', None)
    return str(article_id)

# 上传专栏草稿
@app.route('/special_article_draft',methods=['POST'])
def special_article_draft():
    content=request.form['content']
    ##TODO 文章标题的安全性过滤
    title=request.form['title']
    title_image=request.form['title_image']
    abstract_abstract_with_img=request.form['abstract']
    book_picture=request.form['book_picture']
    book_author=request.form['book_author']
    book_press=request.form['book_press']
    book_page_num=request.form['book_page_num']
    book_price=request.form['book_price']
    book_press_time=request.form['book_press_time']
    book_title=request.form['book_title']
    book_ISBN=request.form['book_ISBN']
    book_binding=request.form['book_binding']
    abstract_plain_text=get_abstract_plain_text(abstract_abstract_with_img)
    if len(abstract_plain_text)<191:
        abstract=abstract_plain_text[0:len(abstract_plain_text)-1]+'......'
    else:
        abstract=abstract_plain_text[0:190]+'......'
    user_id=int(session['user_id'])
    #create_article(title=title,content=content,title_image=title_image,user_id=user_id,article_session_id=session['article_session_id'],is_draft='1',group_id=group_id,category_id=category_id,abstract=abstract)
    book_id=create_book(book_picture=book_picture,book_author=book_author,book_press=book_press,book_page_num=book_page_num,book_price=book_price,book_press_time=book_press_time,book_title=book_title,book_ISBN=book_ISBN,book_binding=book_binding)
    article_id=create_article(title = title, content = content,
	                          title_image = title_image, user_id = user_id,
	                          article_session_id = session['special_article_session_id'],
	                          is_draft ='1', special_id = int(session['special_id']),
	                          group_id = '3', category_id = '0',
	                          abstract = abstract,
	                          book_id = book_id)
    return str(article_id)

##################################  专栏详情页面  ##################################
#TODO 专栏详情尽量改成special detail
@app.route('/special_detail')
def coloum_detail():
	return render_template('special_detail.html')


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

@app.route('/upload_activity_title_image',methods=['GET','POST'])
def save_activity_title_image():
	title_image=request.files['upload_file']
	title_image_name = 'activity_upload_pic_4.png'
	if title_image:
		if allowed_file(title_image.filename):
			title_image_name=get_secure_photoname(title_image.filename)
			title_image_url=os.path.join(app.config['ACTIVITY_TITLE_DEST'], title_image_name)
			title_image.save(title_image_url)
	return app.config['HOST_NAME']+'/upload/activity/activity_title_image/'+title_image_name

#获得文章题图
@app.route('/upload/article/article_title_image/<filename>')
def uploaded_article_title_image(filename):
	return send_from_directory(app.config['ARTICLE_TITLE_DEST'],filename)

#获得活动题图
@app.route('/upload/activity/activity_title_image/<filename>')
def uploaded_activity_title_image(filename):
	return send_from_directory(app.config['ACTIVITY_TITLE_DEST'],filename)


'''
#写文章页面显示
@app.route('/article_upload/group/<int:group_id>/category/<int:category_id>')
@
def article_upload(group_id=3,category_id=4):
	#未登录用户跳转到登录页面，已登录用户，跳转到发表文章页面
	#判断请求链接是否合法
	if group_id in [1,2,3] and category_id in [1,2,3,4]:
		if category_id==4 and group_id!=3:
			abort(404)
		elif category_id<4 and group_id==3:
			abort(404)
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
#写文章页面显示
@app.route('/article_upload')
@login_required
def article_upload():
	article_session_id=get_article_session_id()
	session['article_session_id']=str(article_session_id)
	os.makedirs(os.path.join(app.config['ARTICLE_CONTENT_DEST'], str(article_session_id)))
	role=get_role(int(session['user_id']))
	if role==1:
		upload_url='/group/1/category/'
	elif role==2:
		upload_url='/group/2/category/'
	else:
		abort(404)
	return render_template('test_article_upload.html', upload_url=upload_url)




@app.route('/article_modify/article/<int:article_id>')
def article_modify(article_id):
	article=get_article_information(article_id)
	session['article_session_id']=str(article[0].article_session_id)
	upload_url='/group/'+article[0].groups+'/category/'
	return render_template('test_article_modify.html',article=article[0],book=article[2],upload_url=upload_url)


#打赏作者弹窗
@app.route('/pay_author/<int:article_id>', methods=['GET'])
def pay_author(article_id):
    comment = request.args.get('comment')
    if comment == None:
        comment = ""
    return render_template('pay_author.html', article_id=article_id, comment = comment)

#UEditor配置
@app.route('/editor/<classfication>', methods=['GET', 'POST'])
def upload(classfication):
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
        if classfication=='article':
            path = os.path.join(app.config['ARTICLE_CONTENT_DEST'], session['article_session_id'] ,photoname)
            upfile.save(path)
            result = {
                "state": "SUCCESS",
                "url": "%s/editor_upload/article_session_id/%s/article/%s" % (app.config['HOST_NAME'], str(session['article_session_id']), photoname),
                "title": "article1.jpg",
                "original": "article1.jpg"
            }
            return json.dumps(result)
        else:
            path = os.path.join(app.config['ACTIVITY_CONTENT_DEST'], session['activity_session_id'] ,photoname)
            upfile.save(path)
            result = {
                "state": "SUCCESS",
                "url": "%s/editor_upload/activity_session_id/%s/activity/%s" % (app.config['HOST_NAME'],str(session['activity_session_id']), photoname),
                "title": "article1.jpg",
                "original": "article1.jpg"
            }
            return json.dumps(result)


#获得UEditor内的图片
@app.route('/editor_upload/article_session_id/<article_session_id>/article/<filename>',methods=['GET'])
def editor_upload_article(article_session_id,filename):
	return send_from_directory(os.path.join(app.config['ARTICLE_CONTENT_DEST'],article_session_id), filename)
@app.route('/editor_upload/activity_session_id/<activity_session_id>/activity/<filename>',methods=['GET'])
def editor_upload_activity(activity_session_id,filename):
	return send_from_directory(os.path.join(app.config['ACTIVITY_CONTENT_DEST'],activity_session_id), filename)


#文章完成时的提交路径
##TODO:可能是存在数据库中的草稿提交过来的，这时候只需要把is_draft字段更改就行
@app.route('/article/finish/group/<group_id>/category/<category_id>',methods=['POST'])
def article_finish(group_id,category_id):
	content = request.form['content']
	title = request.form['title']
	##TODO 文章标题的安全性过滤
	title_image=request.form['title_image']
	abstract_abstract_with_img=request.form['abstract']
	book_picture=request.form['book_picture']
	book_author=request.form['book_author']
	book_press=request.form['book_press']
	book_page_num=request.form['book_page_num']
	book_price=request.form['book_price']
	book_press_time=request.form['book_press_time']
	book_title=request.form['book_title']
	book_ISBN=request.form['book_ISBN']
	book_binding=request.form['book_binding']
	abstract_plain_text=get_abstract_plain_text(abstract_abstract_with_img)
	if len(abstract_plain_text)<191:
		abstract=abstract_plain_text[0:len(abstract_plain_text)-1]+'......'
	else:
		abstract=abstract_plain_text[0:190]+'......'
	user_id=int(session['user_id'])
	book_id=create_book(book_picture=book_picture,book_author=book_author,book_press=book_press,book_page_num=book_page_num,book_price=book_price,book_press_time=book_press_time,book_title=book_title,book_ISBN=book_ISBN,book_binding=book_binding)
	article_id=create_article(title=title,content=content,title_image=title_image,user_id=user_id,article_session_id=session['article_session_id'],is_draft='0',group_id=group_id,category_id=category_id,abstract=abstract,book_id=book_id)
	return str(article_id)

#文章草稿的提交路径
@app.route('/article/draft/group/<group_id>/category/<category_id>',methods=['POST'])
def article_draft(group_id,category_id):
	content=request.form['content']
	##TODO 文章标题的安全性过滤
	title=request.form['title']
	title_image=request.form['title_image']
	abstract_abstract_with_img=request.form['abstract']
	book_picture=request.form['book_picture']
	book_author=request.form['book_author']
	book_press=request.form['book_press']
	book_page_num=request.form['book_page_num']
	book_price=request.form['book_price']
	book_press_time=request.form['book_press_time']
	book_title=request.form['book_title']
	book_ISBN=request.form['book_ISBN']
	book_binding=request.form['book_binding']
	abstract_plain_text=get_abstract_plain_text(abstract_abstract_with_img)
	if len(abstract_plain_text)<191:
		abstract=abstract_plain_text[0:len(abstract_plain_text)-1]+'......'
	else:
		abstract=abstract_plain_text[0:190]+'......'
	user_id=int(session['user_id'])
	#create_article(title=title,content=content,title_image=title_image,user_id=user_id,article_session_id=session['article_session_id'],is_draft='1',group_id=group_id,category_id=category_id,abstract=abstract)
	book_id=create_book(book_picture=book_picture,book_author=book_author,book_press=book_press,book_page_num=book_page_num,book_price=book_price,book_press_time=book_press_time,book_title=book_title,book_ISBN=book_ISBN,book_binding=book_binding)
	article_id=create_article(title=title,content=content,title_image=title_image,user_id=user_id,article_session_id=session['article_session_id'],is_draft='1',group_id=group_id,category_id=category_id,abstract=abstract,book_id=book_id)
	return str(article_id)


@app.route('/activity/finish',methods=['POST'])
def activity_finish():
	content=request.form['content']
	title=request.form['title']
	title_image=request.form['title_image']
	activity_time=request.form['activity_time']
	place=request.form['place']
	abstract_abstract_with_img=request.form['abstract']
	abstract_plain_text=get_abstract_plain_text(abstract_abstract_with_img)
	if len(abstract_plain_text)<100:
		abstract=abstract_plain_text[0:len(abstract_plain_text)-1]+'......'
	else:
		abstract=abstract_plain_text[0:100]+'......'
	formatted_time=datetime.strptime(activity_time,"%m/%d/%Y %H:%M")
	activity_id=create_activity(title=title,content=content,title_image=title_image,activity_session_id=session['activity_session_id'],activity_time=formatted_time,abstract=abstract,place=place)
	return str(activity_id)


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


# 收藏专栏
@app.route('/collection_special', methods=['POST'])
def ajax_collection_special():
    try:
        user_id = int(session['user_id'])
    except Exception:
        return "login"

    special_id = int(request.args.get('id'))

    try:
        collection_special(user_id, special_id)

    except Exception:
        return "already"

    return "success"

# 取消收藏专栏
@app.route('/collection_special_cancel', methods=['POST'])
@login_required
def ajax_collection_special_cancel():
    try:
        user_id = int(session['user_id'])
    except Exception:
        return "login"

    special_id = int(request.args.get('id'))

    try:
        collection_special_cancel(user_id, special_id)

    except Exception:
        return "already"

    return "success"


# 收藏专栏作家
@app.route('/collection_special_author', methods=['POST'])
def ajax_collection_special_author():
    try:
        user_id = int(session['user_id'])
    except Exception:
        return "login"

    special_id = int(request.args.get('id'))

    err = collection_special_author(user_id, special_id)
    return err


@app.route('/collection_article',methods=['POST'])
@login_required
def ajax_collection_article():
	article_id=request.form['article_id']
	result=collection_article(user_id=current_user.user_id,article_id=article_id)
	if result=="success":
		update_article_favor(article_id,True)
	return result


@app.route('/collection_activity',methods=['POST'])
@login_required
def ajax_collection_activity():
	if current_user.role==3:
		return 'fail'
	else:
		activity_id=request.form['activity_id']
		result = collection_activity(user_id=current_user.user_id,activity_id=activity_id)
		if result=="success":
			update_activity_favor(activity_id,True)
		return result



# 取消收藏专栏作家
@app.route('/collection_special_author_cancel', methods=['POST'])
def ajax_collection_special_author_cancel():
    try:
        user_id = int(session['user_id'])
    except Exception:
        return "login"

    special_id = int(request.args.get('id'))

    err = collection_special_author_cancel(user_id, special_id)
    return err
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
	update_comment_num(article_id,True)
	time=str(datetime.now()).rsplit('.',1)[0]
	return time

@app.route('/activity/comment',methods=['POST'])
def comment_activity():
	content=request.form['content']
	activity_id=request.form['activity_id']
	create_activity_comment(content,activity_id)
	update_activity_comment_num(activity_id)
	time=str(datetime.now()).rsplit('.',1)[0]
	return time

##################################  文章组  ###################################
@app.route('/article/order_time/group/<int:group_id>/category/<int:category_id>/page/<int:page_id>',methods=['GET'])
@login_required
def article_group_time(group_id,category_id,page_id=1):
	if group_id in [1,2,3] and category_id in [1,2,3,4]:
		if category_id==4 and group_id!=3:
			abort(404)
		elif category_id<4 and group_id==3:
			abort(404)
		else:
			group=GROUP[group_id-1]
			category=CATEGORY[category_id-1]
			order='order_time'
			article_pagination=get_article_pagination_by_time(str(group_id),str(category_id),page_id)
			return render_template('test_article_group.html',group=group,category=category,article_pagination=article_pagination,order=order,group_id=group_id,category_id=category_id)
	else:
		abort(404)

@app.route('/article/order_favor/group/<int:group_id>/category/<int:category_id>/page/<int:page_id>',methods=['GET'])
@login_required
def article_group_favor(group_id,category_id,page_id=1):
	if group_id in [1,2,3] and category_id in [1,2,3,4]:
		if category_id==4 and group_id!=3:
			abort(404)
		elif category_id<4 and group_id==3:
			abort(404)
		else:
			group=GROUP[group_id-1]
			category=CATEGORY[category_id-1]
			order='order_favor'
			article_pagination=get_article_pagination_by_favor(str(group_id),str(category_id),page_id)
			return render_template('test_article_group.html',group=group,category=category,article_pagination=article_pagination,order=order,group_id=group_id,category_id=category_id)
	else:
		abort(404)



##################################	活动 ##################################
##活动主页
@app.route('/activity')
def activity_main():
	current_activity_list=get_current_activity_list(datetime.now())
	passed_activity_list=get_passed_activity_list(datetime.now())
	return render_template('activity.html',current_activity_list=current_activity_list,passed_activity_list=passed_activity_list)

##读取活动
@app.route('/activity/<int:activity_id>')
@login_required
def activity(activity_id):
	activity=get_activity_information(activity_id)
	if activity!=None:
		update_read_num_activity(activity_id)
		comments=get_activity_comments(activity_id)
		return render_template('test_activity.html',activity=activity,avatar=get_avatar(),comments=comments, nick=getNick())
	else:
		abort(404)

##发布活动
@app.route('/activity_upload')
@login_required
def activity_upload():
	if current_user.role!=3:
		abort(404)
	else:
		activity_session_id=get_activity_session_id()
		session['activity_session_id']=str(activity_session_id)
		os.makedirs(os.path.join(app.config['ACTIVITY_CONTENT_DEST'], str(activity_session_id)))
		return render_template('test_activity_upload.html')



##个人主页
@app.route('/homepage')
@login_required
def home_page():
	article_pagination=get_article_pagination_by_user_id(current_user.user_id,True,1)
	return render_template('home_page.html',article_pagination=article_pagination,user=current_user)


##能够返回数据
##返回当前用户所发布的文章
##不是草稿
@app.route('/homepage/pagination/article/page/<int:page_id>',methods=['GET'])
@login_required
def ajax_home_page_article(page_id):
	pagination=get_article_pagination_by_user_id(current_user.user_id,True,page_id)
	has_prev=get_has_prev(pagination)
	has_next=get_has_next(pagination)
	page=str(pagination.page)
	pages=str(pagination.pages)
	return jsonify(has_prev=has_prev,has_next=has_next,page=page,pages=pages,rows=[item.get_serialize() for item in pagination.items])

##能够返回数据
##返回当前用户所发布的评论
@app.route('/homepage/pagination/comment/page/<int:page_id>',methods=['GET'])
@login_required
def ajax_home_page_comment(page_id):
	pagination=get_comment_pagination_by_user_id(current_user.user_id,page_id)
	has_prev=get_has_prev(pagination)
	has_next=get_has_next(pagination)
	page=str(pagination.page)
	pages=str(pagination.pages)
	return jsonify(has_prev=has_prev,has_next=has_next,page=page,pages=pages,rows_comment=[item[0].get_serialize() for item in pagination.items],rows_article=[item[1].get_serialize() for item in pagination.items])


##能够返回数据
##返回当前用户保存的草稿
##点击该文章的题目，应该进入到该文章的编辑页面，路由是/article_modify/article/<int:article_id>
@app.route('/homepage/pagination/article_draft/page/<int:page_id>',methods=['GET'])
@login_required
def ajax_home_page_article_draft(page_id):
	pagination=get_article_draft_pagination(current_user.user_id,page_id)
	has_prev=get_has_prev(pagination)
	has_next=get_has_next(pagination)
	page=str(pagination.page)
	pages=str(pagination.pages)
	return jsonify(has_prev=has_prev,has_next=has_next,page=page,pages=pages,rows=[item.get_serialize() for item in pagination.items])

##能够返回数据
##返回当前用户收藏的文章
@app.route('/homepage/pagination/article_collection/page/<int:page_id>',methods=['GET'])
@login_required
def ajax_home_page_article_collection(page_id):
	pagination=get_article_collection_pagination(current_user.user_id,page_id)
	has_prev=get_has_prev(pagination)
	has_next=get_has_next(pagination)
	page=str(pagination.page)
	pages=str(pagination.pages)
	return jsonify(has_prev=has_prev,has_next=has_next,page=page,pages=pages,rows_article=[item[0].get_serialize() for item in pagination.items],rows_collection_article=[item[1].get_serialize() for item in pagination.items],rows_user=[item[2].get_serialize() for item in pagination.items])


##能够返回数据
##返回当前用户收藏的活动
@app.route('/homepage/pagination/activity_collection/page/<int:page_id>',methods=['GET'])
@login_required
def ajax_home_page_activity_collection(page_id):
	pagination=get_activity_collection_pagination(current_user.user_id,page_id)
	has_prev=get_has_prev(pagination)
	has_next=get_has_next(pagination)
	page=str(pagination.page)
	pages=str(pagination.pages)
	return jsonify(has_prev=has_prev,has_next=has_next,page=page,pages=pages,rows_activity=[item[0].get_serialize() for item in pagination.items],rows_collection_activity=[item[1].get_serialize() for item in pagination.items])


##能够返回数据
##返回当前用户关注的作者
@app.route('/homepage/pagination/user_collection/page/<int:page_id>',methods=['GET'])
@login_required
def ajax_home_page_user_collection(page_id):
	pagination=get_user_collection_pagination(current_user.user_id,page_id)
	has_prev=get_has_prev(pagination)
	has_next=get_has_next(pagination)
	page=str(pagination.page)
	pages=str(pagination.pages)
	return jsonify(has_prev=has_prev,has_next=has_next,page=page,pages=pages,rows_user=[item[0].get_serialize() for item in pagination.items],rows_collection_user=[item[1].get_serialize() for item in pagination.items])

##能够返回数据
##返回当前用户关注的专栏
@app.route('/homepage/pagination/special_collection/page/<int:page_id>',methods=['GET'])
@login_required
def ajax_home_page_special_collection(page_id):
	pagination=get_special_collection_pagination(current_user.user_id,page_id)
	has_prev=get_has_prev(pagination)
	has_next=get_has_next(pagination)
	page=str(pagination.page)
	pages=str(pagination.pages)
	return jsonify(has_prev=has_prev,has_next=has_next,page=page,pages=pages,rows_special=[item[0].get_serialize() for item in pagination.items],rows_collection_special=[item[1].get_serialize() for item in pagination.items])

##能够返回数据
##返回当前用户的粉丝
@app.route('/homepage/pagination/fans/page/<int:page_id>',methods=['GET'])
@login_required
def ajax_home_page_fans(page_id):
	pagination=get_fans_pagination(current_user.user_id,page_id)
	has_prev=get_has_prev(pagination)
	has_next=get_has_next(pagination)
	page=str(pagination.page)
	pages=str(pagination.pages)
	return jsonify(has_prev=has_prev,has_next=has_next,page=page,pages=pages,rows=[item.get_serialize() for item in pagination.items])

##能够返回数据
##返回当前用户接收到的私信
@app.route('/homepage/pagination/message/page/<int:page_id>',methods=['GET'])
@login_required
def ajax_home_page_message(page_id):
	pagination=get_message_pagination(current_user.user_id,page_id)
	has_prev=get_has_prev(pagination)
	has_next=get_has_next(pagination)
	page=str(pagination.page)
	pages=str(pagination.pages)
	return jsonify(has_prev=has_prev,has_next=has_next,page=page,pages=pages,rows_message=[item[0].get_serialize() for item in pagination.items],rows_user=[item[1].get_serialize() for item in pagination.items])

##能够返回数据
##返回当前用户接收到的评论
@app.route('/homepage/pagination/received_comment/page/<int:page_id>',methods=['GET'])
@login_required
def ajax_home_page_received_comment(page_id):
	pagination=get_received_comment_pagination(current_user.user_id,page_id)
	has_prev=get_has_prev(pagination)
	has_next=get_has_next(pagination)
	page=str(pagination.page)
	pages=str(pagination.pages)
	return jsonify(has_prev=has_prev,has_next=has_next,page=page,pages=pages,rows_comment=[item[0].get_serialize() for item in pagination.items],rows_user=[item[1].get_serialize() for item in pagination.items],rows_article=[item[2].get_serialize() for item in pagination.items])

##能够返回数据
##返回当前用户接收到的通知
@app.route('/homepage/pagination/notification/page/<int:page_id>',methods=['GET'])
@login_required
def ajax_home_page_notification(page_id):
	pagination=get_notification_pagination(current_user.user_id,page_id)
	has_prev=get_has_prev(pagination)
	has_next=get_has_next(pagination)
	page=str(pagination.page)
	pages=str(pagination.pages)
	return jsonify(has_prev=has_prev,has_next=has_next,page=page,pages=pages,rows=[item.get_serialize() for item in pagination.items])

##能够返回数据
##返回当前专栏用户的专栏
@app.route('/homepage/pagination/special/page/<int:page_id>',methods=['GET'])
@login_required
def ajax_home_page_special(page_id):
	pagination=get_special_pagination(current_user.user_id,page_id)
	has_prev=get_has_prev(pagination)
	has_next=get_has_next(pagination)
	page=str(pagination.page)
	pages=str(pagination.pages)
	return jsonify(has_prev=has_prev,has_next=has_next,page=page,pages=pages,rows=[item.get_serialize() for item in pagination.items])



##测试成功
##返回操作结果，'birthday_error'、'nick_error'、'success'
@app.route('/homepage/modify/basic_information',methods=['POST'])
@login_required
def ajax_home_page_modify_basic_information():
	user_id=current_user.user_id
	gender=request.form['gender']
	##生日信息的检测
	if request.form['birthday_year']!='' or request.form['birthday_month']!='' or request.form['birthday_day']!='':
		try:
			birthday_year=int(request.form['birthday_year'])
			birthday_month=int(request.form['birthday_month'])
			birthday_day=int(request.form['birthday_day'])
			birthday=date(birthday_year,birthday_month,birthday_day)
			if birthday>=date.today():
				return 'birthday_time_error'
		except:
			return 'birthday_error'
	else:
		birthday=None
	##手机号格式的检测
	phone=request.form['phone']
	if phone!='':
		try:
			int(phone)
		except:
			return 'phone_error'
	else:
		phone=None
	##昵称信息检测
	nick=request.form['nick']
	if len(nick)<2 or len(nick)>10:
		return 'nick_length_error'
	if current_user.nick!=nick and nick_exist(nick):
		return 'nick_error'
	result=updata_user_basic_information_by_user_id(user_id,nick,gender,birthday,phone)
	return result
##测试成功
##修改头像
@app.route('/homepage/modify/avatar',methods=['POST'])
@login_required
def ajax_home_page_modify_avatar():
	avatar=request.form['avatar']
	result=update_user_avatar(current_user.user_id,avatar)
	return result



##测试成功
##返回操作结果，'fail'、'success'
@app.route('/homepage/modify/slogon',methods=['POST'])
@login_required
def ajax_home_page_modify_slogon():
	slogon=request.form['slogon']
	result=update_user_slogon(current_user.user_id,slogon)
	return result

##尚未测试
##修改会员号
##返回操作结果，'fail'、'success'
@app.route('/homepage/modify/member_id',methods=['POST'])
@login_required
def ajax_home_page_modify_member_id():
	member_id=request.form['member_id']
	result=update_member_id(current_user.user_id,member_id)
	return result

##尚未测试
##删除发表的文章
##删除草稿也是这里
##返回操作结果，'fail'、'success'
@app.route('/homepage/delete/article',methods=['POST'])
@login_required
def ajax_home_page_delete_article():
	article_id=request.form['article_id']
	result=delete_article_by_article_id(article_id,current_user.user_id)
	return result


##尚未测试
##删除自己发布的评论
##返回操作结果，'fail'、'success'
@app.route('/homepage/delete/comment',methods=['POST'])
def ajax_home_page_delete_comment():
	comment_id=request.form['comment_id']
	result=delete_comment_by_comment_id(comment_id,current_user.user_id)
	return result

##尚未测试
##删除收藏的活动
##返回操作结果，'fail'、'success'
@app.route('/homepage/delete/collection/activity',methods=['POST'])
def ajax_home_page_delete_collection_activity():
	collection_activity_id=request.form['collection_activity_id']
	result=delete_collection_activity_by_activity_id(collection_activity_id,current_user.user_id)
	return result

##尚未测试
##删除收藏的文章
##返回操作结果，'fail'、'success'
@app.route('/homepage/delete/collection/article',methods=['POST'])
def ajax_home_page_delete_collection_article():
	collection_article_id=request.form['collection_article_id']
	result=delete_collection_article_by_collection_article_id(collection_article_id,current_user.user_id)
	return result

##尚未测试
##删除接收到的私信
##返回操作结果，'fail'、'success'
@app.route('/homepage/delete/message',methods=['POST'])
def ajax_home_page_delete_message():
	message_id=int(request.form['message_id'])
	result=delete_message_by_message_id(message_id,current_user.user_id)
	return result

##尚未测试
##删除接收到的评论
##返回操作结果，'fail'、'success'
@app.route('/homepage/delete/received_comment',methods=['POST'])
def ajax_home_page_delete_received_comment():
	received_comment_id=request.form['comment_id']
	result=delete_received_comment_by_comment_id(received_comment_id,current_user.user_id)
	return result

##尚未测试
##删除专栏
##返回操作结果，'fail'、'success'
@app.route('/homepage/delete/special',methods=['POST'])
def ajax_home_page_delete_special():
	special_id=request.form['special_id']
	result=delete_special_by_special_id(special_id,current_user.user_id)
	return result


##取消关注的作者路由是/collection_cancel/user
##取消关注专栏是由张云昊写的,可以查看一下专栏相关路由
##私信回复的路由是/message
##删除通知就是删除私信
##################################	观点 ##################################
@app.route('/opinion')
def opinion():
	hot_ground_article_list=get_hot_ground_acticle()
	##参数1表示广场
	book_review_list=get_article_group_by_coin('2','1')
	film_review_list=get_article_group_by_coin('2','2')
	essay_list=get_article_group_by_coin('2','3')
	# type表示group_id  type=2表示专栏作家所写文章
	return render_template('layout_article.html', type=2, hot_ground_article_list=hot_ground_article_list,book_review_list=book_review_list,film_review_list=film_review_list,essay_list=essay_list)

##################################	广场 ##################################
#广场主页
@app.route('/square')
def square():
	hot_ground_article_list=get_hot_ground_acticle()
	##参数1表示广场
	book_review_list=get_article_group_by_coin('1','1')
	film_review_list=get_article_group_by_coin('1','2')
	essay_list=get_article_group_by_coin('1','3')
	return render_template('square.html', type=1, hot_ground_article_list=hot_ground_article_list,book_review_list=book_review_list,film_review_list=film_review_list,essay_list=essay_list)


@app.route('/user/<nick>')
@login_required
def view_home_page(nick):
	user=get_user_by_nick(nick)
	if user==None:
		abort(404)
	elif user.user_id==current_user.user_id:
		return redirect(url_for('home_page'))
	else:
		collection=has_collected(user_id=current_user.user_id,another_user_id=user.user_id)
		##默认按时间排序
		article_pagination=get_article_pagination_by_user_id(user.user_id,True,1)
		collection_author_list=get_collection_author_list(user.user_id)
		return render_template('view_home_page.html',user=user,collection=collection,article_pagination=article_pagination,collection_author_list=collection_author_list)

@app.route('/user/<int:user_id>/article/pagination/by_coins/page/<int:page_id>',methods=['GET'])
@login_required
def ajax_article_pagination_by_coins(user_id,page_id):
	article_pagination=get_article_pagination_by_user_id(user_id,False,page_id)
	has_prev=get_has_prev(article_pagination)
	has_next=get_has_next(article_pagination)
	page=str(article_pagination.page)
	pages=str(article_pagination.pages)
	return jsonify(has_prev=has_prev,has_next=has_next,page=page,pages=pages,rows=[article.get_serialize() for article in article_pagination.items])

@app.route('/user/<int:user_id>/article/pagination/by_time/page/<int:page_id>',methods=['GET'])
@login_required
def ajax_article_pagination_by_time(user_id,page_id):
	article_pagination=get_article_pagination_by_user_id(user_id,True,page_id)
	has_prev=get_has_prev(article_pagination)
	has_next=get_has_next(article_pagination)
	page=str(article_pagination.page)
	pages=str(article_pagination.pages)
	return jsonify(has_prev=has_prev,has_next=has_next,page=page,pages=pages,rows=[article.get_serialize() for article in article_pagination.items])



@app.route('/collection/user',methods=['POST'])
@login_required
def collection_user():
	user_id=request.form['user_id']
	if user_id==current_user.user_id:
		return 'fail'
	elif examine_user_id(user_id):
		create_user_collection(another_user_id=user_id,user_id=current_user.user_id)
		return 'success'
	else:
		return 'fail'


@app.route('/collection_cancel/user',methods=['POST'])
@login_required
def cancle_collection_user():
	user_id=request.form['user_id']
	if user_id==current_user.user_id:
		return 'fail'
	elif examine_user_id(user_id):
		delete_user_collection(another_user_id=user_id,user_id=current_user.user_id)
		return 'success'
	else:
		return 'fail'

@app.route('/message',methods=['POST'])
@login_required
def message():
	user_id=request.form['user_id']##接收者的user_id
	content=request.form['content']##私信内容
	if user_id==current_user.user_id:
		return 'fail'
	elif examine_user_id(user_id):
		create_message(to_user_id=user_id,user_id=current_user.user_id,content=content)
		return 'success'
	else:
		return 'fail'


@app.route('/award',methods=['POST'])
@login_required
def award_article():
	article_id=request.form['article_id']
	try:
		award_num=int(request.form['award_num'])
	except:
		result="fail"
		return result
	if current_user.coin<award_num or award_num<=0:
		result="fail"
	else:
		result=process_article_award(user_id=current_user.user_id,article_id=article_id,award_num=award_num)
	return result




##################################	已废弃 ##################################

##################################	article_test ##################################
@app.route('/pay_author')
def article_test():
	return render_template('pay_author.html')

@app.route('/message_page/<int:to_user_id>/')
@login_required
def message_page(to_user_id):
	return render_template('message_page.html', to_user_id=to_user_id)

@app.route('/verify_remind/')
@login_required
def verify_remind():
	return render_template('verify_remind.html')

@app.route('/verify_email_again/',methods=['GET'])
@login_required
def verify_email_again():
	send_verify_email(current_user.nick, current_user.password, current_user.email)
	return 'success'
