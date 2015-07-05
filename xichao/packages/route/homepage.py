# -*- coding: utf-8 -*-
from imports import *

@app.route('/message_page/<int:to_user_id>/')
@login_required
def message_page(to_user_id):
    return render_template('message_page.html', to_user_id=to_user_id)

#root user send notification
@app.route('/notification_page')
@login_required
def notification_page():
    if current_user.role!=3:
        abort(404)
    else:
        return render_template('notification_page.html')

#接收上传的封面文件，保存并返回路径
@app.route('/upload/cover',methods=['POST'])
def save_cover():
    cover=request.files['cover']
    cover_name='default.jpg'
    if cover:
        if allowed_file(cover.filename):
            cover_name=get_secure_photoname(cover.filename)
            cover_url=os.path.join(app.config['COVER_DEST'],cover_name)
            cover.save(cover_url)
    return '/upload/cover/'+cover_name

#为上传的封面文件提供服务
@app.route('/upload/cover/<filename>')
def uploaded_cover(filename):
    return send_from_directory(app.config['COVER_DEST'],filename)


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
        #collection_author_list=get_collection_author_list(user.user_id)
        article_number=get_article_number(user.user_id)
        return render_template('view_home_page_new.html',user=user,collection=collection,article_pagination=article_pagination,article_number=article_number)

@app.route('/user/<int:user_id>/collection_author/pagination/page/<int:page_id>',methods=['GET'])
@login_required
def ajax_collection_user_pagination(user_id,page_id):
    pagination=get_user_collection_pagination(user_id,page_id)
    has_prev=get_has_prev(pagination)
    has_next=get_has_next(pagination)
    page=str(pagination.page)
    pages=str(pagination.pages)
    return jsonify(has_prev=has_prev,has_next=has_next,page=page,pages=pages,rows_user=[item[0].get_serialize() for item in pagination.items],rows_collection_user=[item[1].get_serialize() for item in pagination.items])


@app.route('/user/<int:user_id>/comment/pagination/page/<int:page_id>',methods=['GET'])
def ajax_comment_pagination(user_id,page_id):
    pagination=get_comment_pagination_by_user_id(user_id,page_id)
    has_prev=get_has_prev(pagination)
    has_next=get_has_next(pagination)
    page=str(pagination.page)
    pages=str(pagination.pages)
    return jsonify(has_prev=has_prev,has_next=has_next,page=page,pages=pages,rows_comment=[item[0].get_serialize() for item in pagination.items],rows_article=[item[1].get_serialize() for item in pagination.items])


@app.route('/user/<int:user_id>/article/pagination/by_coins/page/<int:page_id>',methods=['GET'])
@login_required
def ajax_article_pagination_by_coins(user_id,page_id):
    article_pagination=get_article_pagination_by_user_id(user_id,False,page_id)
    has_prev=get_has_prev(article_pagination)
    has_next=get_has_next(article_pagination)
    page=str(article_pagination.page)
    pages=str(article_pagination.pages)
    rows=[article.get_serialize() for article in article_pagination.items]
    return jsonify(has_prev=has_prev,has_next=has_next,page=page,pages=pages,rows=rows)

@app.route('/user/<int:user_id>/article/pagination/by_time/page/<int:page_id>',methods=['GET'])
@login_required
def ajax_article_pagination_by_time(user_id,page_id):
    article_pagination=get_article_pagination_by_user_id(user_id,True,page_id)
    has_prev=get_has_prev(article_pagination)
    has_next=get_has_next(article_pagination)
    page=str(article_pagination.page)
    pages=str(article_pagination.pages)
    rows=[article.get_serialize() for article in article_pagination.items]
    return jsonify(has_prev=has_prev,has_next=has_next,page=page,pages=pages,rows=rows)


##个人主页
@app.route('/homepage')
@login_required
def home_page():
    article_pagination=get_article_pagination_by_user_id(current_user.user_id,True,1)
    article_number=get_article_number(current_user.user_id)
    if current_user.member_id==None:
        point=0
    else:
        point=get_point_by_member_id(current_user.member_id)
    return render_template('home_page_new.html',article_pagination=article_pagination,user=current_user,article_number=article_number,point=point)


##能够返回数据
##返回当前用户所发布的文章
##不是草稿
@app.route('/homepage/pagination/article/page/<int:page_id>',methods=['GET'])
@login_required
def ajax_home_page_article(page_id):
    sort=request.args.get('sort')
    if sort=="by_time":
        sort_by=True
    else:
        sort_by=False
    pagination=get_article_pagination_by_user_id(current_user.user_id,sort_by,page_id)
    rows = [item.get_serialize() for item in pagination.items]

    has_prev=get_has_prev(pagination)
    has_next=get_has_next(pagination)
    page=str(pagination.page)
    pages=str(pagination.pages)
    return jsonify(has_prev=has_prev,has_next=has_next,page=page,pages=pages,rows=rows)

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
    ##未读信息打上标记
    result=jsonify(has_prev=has_prev,has_next=has_next,page=page,pages=pages,rows_message=[item[0].get_serialize() for item in pagination.items],rows_user=[item[1].get_serialize() for item in pagination.items])
    update_message_read_state(pagination)
    return result

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
    ##未读信息打上标记
    result=jsonify(has_prev=has_prev,has_next=has_next,page=page,pages=pages,rows_comment=[item[0].get_serialize() for item in pagination.items],rows_user=[item[1].get_serialize() for item in pagination.items],rows_article=[item[2].get_serialize() for item in pagination.items])
    update_comment_read_state(pagination)
    return result

##能够返回数据
##返回当前用户接收到的通知
@app.route('/homepage/pagination/notification/page/<int:page_id>',methods=['GET'])
@login_required
def ajax_home_page_notification(page_id):
    pagination=get_notification_pagination(current_user.user_id,page_id)
    ##update_notification_read_state(pagination)
    has_prev=get_has_prev(pagination)
    has_next=get_has_next(pagination)
    page=str(pagination.page)
    pages=str(pagination.pages)
    ##未读信息打上标记
    result=jsonify(has_prev=has_prev,has_next=has_next,page=page,pages=pages,rows=[item.get_serialize() for item in pagination.items])
    update_notification_read_state(pagination)
    return result

##能够返回数据
##返回专栏用户的专栏
@app.route('/homepage/pagination/special/page/<int:page_id>/user/<int:user_id>',methods=['GET'])
@login_required
def ajax_home_page_special(page_id, user_id):
    pagination=get_special_pagination(user_id,page_id)
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

@app.route('/homepage/modify/cover',methods=['POST'])
@login_required
def ajax_home_page_modify_cover():
    cover=request.form['cover']
    result=update_user_cover(current_user.user_id,cover)
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
    article_id=request.form['item_id']
    result=delete_article_by_article_id(article_id,current_user.user_id)
    return result


##尚未测试
##删除自己发布的评论
##返回操作结果，'fail'、'success'
@app.route('/homepage/delete/comment',methods=['POST'])
def ajax_home_page_delete_comment():
    comment_id=request.form['item_id']
    result=delete_comment_by_comment_id(comment_id,current_user.user_id)
    return result

##尚未测试
##删除收藏的活动
##返回操作结果，'fail'、'success'
@app.route('/homepage/delete/collection/activity',methods=['POST'])
def ajax_home_page_delete_collection_activity():
    collection_activity_id=request.form['item_id']
    result=delete_collection_activity_by_activity_id(collection_activity_id,current_user.user_id)
    return result

##尚未测试
##删除收藏的文章
##返回操作结果，'fail'、'success'
@app.route('/homepage/delete/collection/article',methods=['POST'])
def ajax_home_page_delete_collection_article():
    collection_article_id=request.form['item_id']
    result=delete_collection_article_by_collection_article_id(collection_article_id,current_user.user_id)
    return result

##尚未测试
##删除接收到的私信
##返回操作结果，'fail'、'success'
@app.route('/homepage/delete/message',methods=['POST'])
def ajax_home_page_delete_message():
    message_id=int(request.form['item_id'])
    result=delete_message_by_message_id(message_id,current_user.user_id)
    return result

##尚未测试
##删除接收到的评论
##返回操作结果，'fail'、'success'
@app.route('/homepage/delete/received_comment',methods=['POST'])
def ajax_home_page_delete_received_comment():
    received_comment_id=request.form['item_id']
    result=delete_received_comment_by_comment_id(received_comment_id,current_user.user_id)
    return result

##尚未测试
##删除专栏
##返回操作结果，'fail'、'success'
@app.route('/homepage/delete/special',methods=['POST'])
def ajax_home_page_delete_special():
    special_id=request.form['item_id']
    result=delete_special_by_special_id(special_id,current_user.user_id)
    return result