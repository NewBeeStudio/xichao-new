# -*- coding: utf-8 -*-
from imports import *
from xichao.packages.config.membership import _MEMBERSHIP_READ_, _MEMBERSHIP_WRITE_

#from xichao.packages.config import *#_MEMBERSHIP_READ_, _MEMBERSHIP_WRITE_

#from xichao.packages.config import _MEMBERSHIP_READ_, _MEMBERSHIP_WRITE_
#from xichao.packages.config import _ROLE_Normal_, _ROLE_Author_, _ROLE_Editor_, _ROLE_Root_
#from xichao.packages.config import _GROUP_Square_, _GROUP_Article_, _GROUP_Special_
#from xichao.packages.config import _CATEGORY_BookReview_, _CATEGORY_FilmReview_, _CATEGORY_Essay_

################################## 会员卡绑定 ##################################

@app.route('/membercard_associate', methods=['GET', 'POST'])
@login_required
def membercard_associate():
    # myCaptcha = captcha.Captcha()
    form = MembercardForm(request.form)
    if request.method == 'POST' and form.validate():
        user = db_session.query(User).filter_by(user_id = current_user.user_id).all()[0]
        user.member_id = form.cardID.data
        db_session.commit()

#        flash(u'绑定成功，正在跳转')
        time.sleep(5)
        return redirect(url_for('index'))
    return render_template('layer_membercard_associate.html', form=form)

@app.route('/membercard_validate', methods=['GET'])
@login_required
def membercard_validate():
    try:
        cardID = request.args.get('cardID')
        name = request.args.get('name')
        email = request.args.get('email')
    except Exception:
        return "fail"

    #import urllib, json
    # TODO
    member_data = urllib.urlopen(_MEMBERSHIP_READ_ + cardID).read()
    if member_data[:4] == "fail":
        return "fail"
    member_data =  member_data.split('}')[0]+'}'
    #member_data = '{"cardID":"141034", "name":"张云昊", "email":"zhangyunh@gmail.com", "coin":"616"}'
    memberDB = json.loads(member_data)
    if memberDB['name'] == "":
            return "name null"
    if memberDB['email'] == "":
            return "email null"
    if memberDB['name'] == name and memberDB['email'] == email:
        return memberDB['coin']
    else:
        if memberDB['name'] != name:
            return "name"
        if memberDB['email'] != email:
            return "email"

@app.route('/member_information',methods=['GET'])
@login_required
def member_information():
    member_data = urllib.urlopen(_MEMBERSHIP_READ_ + current_user.member_id).read()
    member_data =  member_data.split('}')[0]+', "webcoin":"'+str(current_user.coin)+'"}'
    memberDB = json.loads(member_data)
    return json.dumps(memberDB)

##################################  会员卡积分与曦潮币互换  ##################################
@app.route('/coin_to_point',methods=['POST'])
@login_required
def coin_to_point():
    if current_user.member_id==None:
        return 'member_fail'
    else:
        amount_str=request.form['coin_conversion_amount']
        try:
            amount=int(amount_str)
        except Exception, e:
            return 'number_fail'
        if amount>current_user.coin or amount<0:
            return 'amount_fail'
        else:
            try:
                result=urllib.urlopen(_MEMBERSHIP_WRITE_ + current_user.member_id+'&Delta='+amount_str).read()
            except:
                return 'fail'
            if result[:7]=="Success":
                user_coin_sub(current_user.user_id,amount)
                return 'success'     
            else:
                return 'fail'

@app.route('/point_to_coin',methods=['POST'])
@login_required
def point_to_coin():
    if current_user.member_id==None:
        return 'member_fail'
    else:
        amount_str=request.form['point_conversion_amount']
        try:
            amount=int(amount_str)
        except Exception, e:
            return 'number_fail'
        point=get_point_by_member_id(current_user.member_id)
        if amount>point or amount<0:
            return 'amount_fail'
        else:
            try:
                result=urllib.urlopen(_MEMBERSHIP_WRITE_ + current_user.member_id+'&Delta=-'+amount_str).read()
            except:
                return 'fail'
            if result[:7]=="Success":
                user_coin_add(current_user.user_id,amount)
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
@app.route('/ajax_membercard', methods=['GET'])
def ajax_register_membercard():
    cardID = request.args.get('cardID',0,type=unicode)
    name = request.args.get('name',0,type=unicode)
    email = request.args.get('email',0,type=unicode)

    request_form_from_ajax = ImmutableMultiDict([('cardID', cardID),('name', name), ('email', email)])
    form = MembercardForm(request_form_from_ajax)
    form.validate()

    errors_return = {} #返回去的错误信息字典
    for param in ['cardID', 'name', 'email']:
        if form.errors.get(param) == None:
            errors_return[param] = [u'']
        else:
            errors_return[param] = form.errors.get(param)
            print errors_return[param][0]

    return jsonify(email=errors_return.get('email')[0],
                   name=errors_return.get('name')[0],
                   cardID=errors_return.get('cardID')[0])
