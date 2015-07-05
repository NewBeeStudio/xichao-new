# -*- coding: utf-8 -*-
from imports import *

@app.route('/')
def default():
    return redirect(url_for('index'))

@app.route('/index')
def index():
    homepage_special_list, slideUrl = get_homepage_specials()
    most_hot_activity=get_most_hot_activity()
    hot_articles = get_hot_articles(10)
    latest_articles = get_latest_articles(10)
    user_focus = get_all_focus_article(10)#current_user.user_id)
    return render_template('template.html', special_list = homepage_special_list,
                                            hot_articles = hot_articles,
                                            articles = get_special_article,
                                            slideUrl = slideUrl,
                                            get_special_author = get_special_author,
                                            get_author = get_nick_by_userid,
                                            most_hot_activity=most_hot_activity,
                                            user_focus = user_focus,
                                            latest_articles = latest_articles,
                                            get_special_information = get_special_information,
                                            logged_in = ('user_id' in session))

## 修改首页
@app.route('/modify_homepage')
@login_required
def modify_homepage():
    if (not root_authorized()):
        abort(404)
    allSpecial = get_all_special()
    return render_template('modify_homepage.html', allSpecial = allSpecial)

## 完成首页修改
@app.route('/modify_homepage_finish', methods=['GET'])
@login_required
def modify_homepage_finish():
    if (not root_authorized()):
        abort(404)
    special1 = request.args.get('special1')
    special2 = request.args.get('special2')
    special3 = request.args.get('special3')
    special4 = request.args.get('special4')

    url1 = request.args.get('url1')
    url2 = request.args.get('url2')
    url3 = request.args.get('url3')
    url4 = request.args.get('url4')

    recommend_actctivity = request.args.get('recommend_activity')

    return modify_homepage_func(special1, url1,
                                special2, url2,
                                special3, url3,
                                special4, url4,
                                recommend_actctivity)

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

@app.route('/notify',methods=['POST'])
@login_required
def notify():
    if current_user.role!=3:
        return 'fail'
    else:
        content=request.form['content']
        create_notification(user_id=current_user.user_id,content=content)
        return 'success'



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

@app.route('/ajax_news',methods=['GET'])
def ajax_news():
    if current_user.is_anonymous():
        all_message_number=0
        message_number=0
        comment_number=0
        notification_number=0
    else:
        message_number=get_message_number(current_user.user_id)
        comment_number=get_comment_number(current_user.user_id)
        notification_number=get_notification_number(current_user.user_id)
        all_message_number=message_number+comment_number+notification_number
    return jsonify(all_message_number=str(all_message_number),message_number=str(message_number),comment_number=str(comment_number),notification_number=str(notification_number))

@app.route('/suggest_page/')
@login_required
def suggest_page():
    return render_template('suggest_page.html', to_user_id=get_suggest_user().user_id)
