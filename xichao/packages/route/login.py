# -*- coding: utf-8 -*-
from imports import *

#######################################  注销  #########################################
@app.route('/logout')
@login_required
def logout():
    #弹出sessio
    # session.pop('user', None)
    logout_user()
    
    response=make_response(redirect(url_for('index')))
    #删除cookie，flask-login已完成相应操作
   
    return response

##################################  登陆  ##################################
##TODO：cookie的过期时间
@app.route('/login',methods=['GET','POST'])
def login():
    if not current_user.is_anonymous():
        return redirect(url_for("index"))
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
            

            response=make_response(redirect(request.form.get("request_url") or url_for("index")))
            #if form.stay.data:
            #    response.set_cookie('user',nick)
            return response
        else:
            error=u'邮箱或密码错误'
    return render_template('login.html', request_url=request.form.get("request_url"), form=form, error=error)

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

####################################  注册  ##################################
@app.route('/register', methods=['GET', 'POST'])
def register():
    # myCaptcha = captcha.Captcha()
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():

        user = User(nick=form.nick.data, email=form.email.data, role=1, register_time=datetime.now(), last_login_time=datetime.now(), password=encrypt(form.password.data),state='0',photo=request.form['avatar'],slogon='暂未填写')

        db_session.add(user)
        db_session.commit()
        #需要增加异常处理，捕获异常，
        send_verify_email(form.nick.data,encrypt(form.password.data),form.email.data)
        # session['user']=request.form['nick']
        user=User.query.filter_by(email=form.email.data).first()
        login_user(user)
        time.sleep(3)
        return redirect(url_for('index'))
    return render_template('register.html', form=form)

@app.route('/_getImage')
def getCaptcha():
    return captcha.create_validate_code()


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

##################################  忘记密码  ##################################
@app.route('/forgetPassword',methods=['GET', 'POST'])
def forgetPassword():
    error = None
    form = ForgetPasswordForm(request.form)
    
    if request.method == 'POST' and form.validate():
        nick = get_nick_by_email(form.email.data)
        password = get_password_by_email(form.email.data)
        send_resetpassword_email(nick, password, form.email.data) #待修改
        flash(u'我们已向你的注册邮箱发送了密码重置邮件,请至邮箱查收')
        return render_template('forgetPassword.html', form = form, error = error)

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

@app.route('/verify_remind/')
@login_required
def verify_remind():
    return render_template('verify_remind.html')

@app.route('/verify_email_again/',methods=['GET'])
@login_required
def verify_email_again():
    if send_verify_email(current_user.nick, current_user.password, current_user.email):
        return 'success'
    else:
        return 'fail'

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
    success = True
    for param in ['email', 'nick', 'password', 'confirm']:
        if form.errors.get(param) == None:
            errors_return[param] = [u'']
        else:
            errors_return[param] = form.errors.get(param)
            success = False

    return jsonify(email=errors_return.get('email')[0],nick=errors_return.get('nick')[0],password=errors_return.get('password')[0],confirm=errors_return.get('confirm')[0],success=success)
