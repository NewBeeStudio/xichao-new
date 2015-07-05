# -*- coding: utf-8 -*-
from imports import *

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
        view = 'all'
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
        specials_pagination = get_all_specials(sort, page_id, 12)
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
                                                  author = get_special_author)

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
    author = get_special_author(special.special_id)

#    print ddd
    #article的分页对象，articles_pagination.items获得该分页对象中的所有内容，为一个list
    login_user = get_userid_from_session()

    articles_pagination = get_special_article(special_id, page_id, sort, 5)
    related_other_special = get_related_special(special.special_id)

    is_mobile = is_small_mobile_device(request)

    if is_mobile:
        return render_template('mobile_special_detail.html',
                            login_user_id = login_user,
                            is_mobile = is_mobile,
                            root_authorized = root_authorized(),
                            #author_itself = (special.user_id == login_user),
                            has_collected_special = get_special_collect_info(login_user, special_id),
                            has_collected_author = has_collected,
                            sort_change_url = sort_change_url,
                            special_id = special_id,
                            sort = sort,
                            special_favor = special.favor,
                            special_title = special.name,
                            special_author = author,
                            #special_author_slogon = author.slogon,
                            special_introduction = special.introduction,
                            special_style = special.style,
                            special_total_issue = special.total_issue,
                            special_update_frequency = special.update_frequency,
                            special_coin = special.coin,
                            special_image = special.picture,
                            #special_author_avatar = author.photo,
                            articles_pagination = articles_pagination,
                            get_nick_by_userid = get_nick_by_userid)
    else:
        return render_template('special_detail.html',
                            len = len,
                            author = get_special_author,
                            login_user_id = login_user,
                            is_mobile = is_mobile,
                            root_authorized = root_authorized(),
                            #author_itself = (special.user_id == login_user),
                            has_collected_special = get_special_collect_info(login_user, special_id),
                            has_collected_author = has_collected,
                            sort_change_url = sort_change_url,
                            special_id = special_id,
                            sort = sort,
                            other = get_special_author_other,
                            special_favor = special.favor,
                            special_title = special.name,
                            special_author = author,
                            #special_author_slogon = author.slogon,
                            special_introduction = special.introduction,
                            special_style = special.style,
                            special_total_issue = special.total_issue,
                            special_update_frequency = special.update_frequency,
                            special_coin = special.coin,
                            special_image = special.picture,
                            #special_author_avatar = author.photo,
                            articles_pagination = articles_pagination,
                            related_other_special = related_other_special,
                            get_nick_by_userid = get_nick_by_userid)

## 创建专栏界面
@app.route('/create_special')
@login_required
def create_special():
    if (not root_authorized()):
        abort(404)
    return render_template('create_special.html')


## 修改专栏界面
@app.route('/modify_special')
@login_required
def modify_special():
    if (not root_authorized()):
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
    if (not root_authorized()):
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

    authors = []
    try:
        author_list = eval(request.args.get('author_list'))
        for nick in author_list:
            author = get_userid_by_nick(nick)
            if (len(author) == 0):
                return "nick_error"
            authors.append(author[0][0])
    except Exception:
        return "failed"

    special_id = create_new_special(name = title,
                       #user_id = author[0][0],
                       picture = title_image,
                       introduction = content,
                       style = style,
                       total_issue = total_issue,
                       update_frequency = update_frequency)
    for author in authors:
        create_new_special_author(special_id, author)

    return str(special_id)

## 完成修改专栏
@app.route('/modify_special_finish', methods=['GET'])
@login_required
def modify_special_finish():
    if (not root_authorized()):
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

    authors = []
    try:
        author_list = eval(request.args.get('author_list'))
        for nick in author_list:
            author = get_userid_by_nick(nick)
            if (len(author) == 0):
                return "nick_error"
            authors.append(author[0][0])
    except Exception:
        return "failed"

    try:
        special_id = modify_special_func(name = title,
                                         #user_id = author[0][0],
                                         authors = authors,
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

    ####TODO
    #author = get_special_information(special_id).user_id
    #login_user = get_userid_from_session()
    if (not root_authorized()):
        abort(404)

    article_session_id = get_article_session_id()
    session['special_article_session_id'] = str(article_session_id)
    session['special_id'] = str(special_id)
    os.makedirs(os.path.join(app.config['ARTICLE_CONTENT_DEST'], str(article_session_id)))

    return render_template('special_article_upload.html')

# 修改专栏文章
@app.route('/special_article_modify/article/<int:article_id>')
@login_required
def special_article_modify(article_id):
    article = get_article_information(article_id)

    try:
        special_id = int(article[0].special_id)
    except Exception:
        abort(404)

    if (not root_authorized()):
        abort(404)

    session['special_id'] = str(article[0].special_id)
    session['special_article_session_id'] = str(article[0].article_session_id)
    return render_template('special_article_modify.html',
                            article=article[0], book=article[2],
                            get_author = get_nick_by_userid)


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

    special_author = request.form['special_author']

    try:
        user_id = get_userid_by_nick(special_author)[0][0]
        if not has_special_author(int(session['special_id']), user_id):
            raise Exception
    except Exception:
        return "nick"

    abstract_plain_text=get_abstract_plain_text(abstract_abstract_with_img)
    if len(abstract_plain_text)<191:
        abstract=abstract_plain_text[0:len(abstract_plain_text)-1]+'......'
    else:
        abstract=abstract_plain_text[0:190]+'......'
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
    
    special_author = request.form['special_author']
    try:
        user_id = get_userid_by_nick(special_author)[0][0]
        if not has_special_author(int(session['special_id']), user_id):
            raise Exception
    except Exception:
        return "nick"

    abstract_plain_text=get_abstract_plain_text(abstract_abstract_with_img)
    if len(abstract_plain_text)<191:
        abstract=abstract_plain_text[0:len(abstract_plain_text)-1]+'......'
    else:
        abstract=abstract_plain_text[0:190]+'......'

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
@app.route('/upload/special/<filename>')
def uploaded_special_image(filename):
    return send_from_directory(app.config['SPECIAL_DEST'],filename)
