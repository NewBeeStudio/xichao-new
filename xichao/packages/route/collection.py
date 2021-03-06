# -*- coding: utf-8 -*-
from imports import *
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

    author_id = int(request.form['author'])

    err = collection_special_author(user_id, author_id)
    return err
# 取消收藏专栏作家
@app.route('/collection_special_author_cancel', methods=['POST'])
def ajax_collection_special_author_cancel():
    try:
        user_id = int(session['user_id'])
    except Exception:
        return "login"

    author_id = int(request.form['author'])

    err = collection_special_author_cancel(user_id, author_id)
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