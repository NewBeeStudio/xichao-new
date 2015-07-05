# -*- coding: utf-8 -*-
from imports import *

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
#@login_required
def article(article_id):
    is_mobile = is_small_mobile_device(request)
    is_login = 'user_id' in session
    if not is_mobile and not is_login:
        return redirect(url_for('login'))

    comment_page=request.args.get("comment_page")
    if not comment_page:
        comment_page=1
    #if comment_page
    article=get_article_information(article_id)
    comment_page=get_article_comments_pagination(article_id,int(comment_page),5)
    comment_reply=[]
    
    for item in comment_page.items:
        tmp=get_comment_reply(article_id,int(item[0].comment_id))
        for i in range(0,len(tmp)):
            tmp[i]=tmp[i]+(get_nick_by_userid(tmp[i][0].to_user_id),)
            
        comment_reply.append(tmp)
    
    if article!=None:
        if article[0].is_draft=='1' and article[1].user_id!=current_user.user_id:
            abort(404)
        else:
            session['article_session_id']=article[0].article_session_id
            comments=get_article_comments(article_id)
            try:
                comment_num = len(comments);
            except:
                comment_num = 0;
            if(article[0].groups == '3'):
                special = get_special_information(article[0].special_id);
            else:
                special = 0;
            """
            if article[0].user_id==current_user.user_id:
                pass
            else:
                update_read_num(article_id)
            """

            prev_article = prev_special_article(article_id)
            next_article = next_special_article(article_id)

            if is_mobile:
                if is_login:
                    nick = getNick()
                else:
                    nick = ""
                return render_template('mobile_test_article.html',
                root_authorized = root_authorized(),
                article=article[0], author=article[1],
                prev_article = prev_article,
                next_article = next_article,
                book=article[2], avatar=get_avatar(),
                comments=comments, comment_page=comment_page,
                comment_reply=comment_reply, nick=nick,
                special_info = get_special_information)
            else:
                return render_template('test_article.html',
                root_authorized = root_authorized(),
                article=article[0], author=article[1],
                prev_article = prev_article,
                next_article = next_article,
                book=article[2], avatar=get_avatar(),
                comments=comments, comment_page=comment_page,
                comment_reply=comment_reply, nick=getNick(),
                special_info = get_special_information)


    else:
        abort(404)

@app.route('/article/<int:article_id>/comment/page/<int:page_id>',methods=['GET'])
@login_required
def ajax_article_comments(article_id,page_id):
    comment_page=get_article_comments_pagination(article_id,int(page_id),5)
    comments_row=[]
    comment_reply=[]

    for item in comment_page.items:
        comments_row.append([item[0].get_serialize(),item[1],item[2],item[3]])
    #print comments_row

    for item in comment_page.items:
        one=get_comment_reply(article_id,int(item[0].comment_id))
        if one ==[]:
            comment_reply.append([])
        else:
            reply=[com[0].get_serialize() for com in one]
            comment_reply.append([reply,item[1],item[2],item[3]])
    
    return jsonify(comment_page=str(comment_page.page),comments_row=comments_row,comment_reply=comment_reply)

@app.route('/comment_remove/<int:comment_id>',methods=['GET'])
@login_required
def ajax_comments_remove(comment_id):
    delete_comment_by_comment_id(comment_id, current_user.user_id)
    return "success"

@app.route('/get_nick/<int:user_id>',methods=['GET'])
@login_required
def ajax_get_nick(user_id):
    return jsonify(user_id=user_id,user_nick=get_nick_by_userid(user_id))

#打赏作者弹窗
@app.route('/pay_author/<int:article_id>', methods=['GET'])
def pay_author(article_id):
    comment = request.args.get('comment')
    if comment == None:
        comment = ""
    return render_template('pay_author.html', article_id=article_id, comment = comment)
#回复评论弹窗
@app.route('/reply_to/<int:article_id>', methods=['GET'])
def reply_to(article_id):
    to_user_id = request.args.get('to_user_id')
    reply_to_comment_id = request.args.get('reply_to_comment_id')
    to_user_nick=get_nick_by_userid(to_user_id)
    
    return render_template('reply_to.html', article_id=article_id, to_user_id=to_user_id, reply_to_comment_id=reply_to_comment_id,to_user_nick = to_user_nick)

##################################    评论处理 ##################################
@app.route('/article/comment',methods=['POST'])
def comment():
    content=request.form['content']
    to_user_id=request.form['to_user_id']
    article_id=request.form['article_id']
    reply_to_comment_id=request.form['reply_to_comment_id']

    create_comment(content,to_user_id,article_id,reply_to_comment_id)
    update_comment_num(article_id,True)
    time=str(datetime.now()).rsplit('.',1)[0]
    comment_id=get_current_comment_id()
    return jsonify(time=time,comment_id=comment_id)

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