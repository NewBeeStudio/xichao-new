# -*- coding: utf-8 -*-
from imports import *
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
        upload_url='/group/1/category/'
        # 原来是 upload_url='/group/2/category/'
        # 第一版没有“观点”
    else:
        abort(404)
    return render_template('test_article_upload.html', upload_url=upload_url)

@app.route('/article_modify/article/<int:article_id>')
@login_required
def article_modify(article_id):
    article=get_article_information(article_id)
    session['article_session_id']=str(article[0].article_session_id)
    upload_url='/group/'+article[0].groups+'/category/'
    
    if (article[0].user_id != current_user.user_id):
        abort(404)

    return render_template('test_article_modify.html',article=article[0],book=article[2],upload_url=upload_url)



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
            print "\n\n\n\n\n\n\n\n######################\n\n\n\n\n\n\n\n"+"\n\n\n"
            upfile.save(path)
            result = {
                "state": "SUCCESS",
                #"url": "%s/editor_upload/article_session_id/%s/article/%s" % (app.config['HOST_NAME'], str(session['article_session_id']), photoname),
                "url": "/editor_upload/article_session_id/%s/article/%s" % (str(session['article_session_id']), photoname),
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
    article_id=create_article(title=title,content=content,title_image=title_image,user_id=user_id,article_session_id=session['article_session_id'],is_draft='0',group_id=1,category_id=category_id,abstract=abstract,book_id=book_id)
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

##################################    活动 ##################################
##活动主页
@app.route('/activity')
def activity_main():
#    current_activity_list=get_current_activity_list(datetime.now())
#    passed_activity_list=get_passed_activity_list(datetime.now())
#    return render_template('activity.html',current_activity_list=current_activity_list,passed_activity_list=passed_activity_list)
    try:
        sort = request.args.get('sort')
        page_id = int(request.args.get('page'))
    except Exception:
        abort(404)

    if sort != 'favor':
        sort = 'time'
        sort_change_url = '/activity?sort=favor&page=1'
    else:
        sort_change_url = '/activity?sort=time&page=1'
    current_activity_list=get_current_activity_list(datetime.now())
    passed_activity_list=get_passed_activity_pagination(sort, page_id, 5)
    return render_template('activity.html', sort = sort, 
                            sort_change_url = sort_change_url,
                            current_activity_list = current_activity_list,
                            passed_activity_list = passed_activity_list)

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
