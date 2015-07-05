# -*- coding: utf-8 -*-
from imports import *

##################################  收藏/取消收藏 专栏  ####################################
def collection_special(user_id, special_id):
    query = db_session.query(Collection_Special).filter_by(user_id = user_id, special_id = special_id).all()
    if len(query) == 0:
        collect_spe = Collection_Special(user_id = user_id, 
                                         special_id = special_id,
                                         time = datetime.now())
        query = db_session.query(Special).filter_by(special_id = special_id).all()[0]
        query.favor += 1
        
        db_session.add(collect_spe)
        db_session.commit()
        
    else:
        raise Exception

def collection_special_cancel(user_id, special_id):
    query = db_session.query(Collection_Special).filter_by(user_id = user_id, special_id = special_id).all()
    if len(query) != 0:
        db_session.delete(query[0])
        query = db_session.query(Special).filter_by(special_id = special_id).all()[0]
        query.favor -= 1
        db_session.commit()
        
    else:
        raise Exception

        
##################################  收藏/取消收藏 专栏作家  ####################################
def collection_special_author(user_id, author_id):
    another_user_id = author_id
    if (user_id == another_user_id):
        return "self"
    query = db_session.query(Collection_User).filter_by(user_id = user_id, another_user_id = another_user_id).all()
    if len(query) == 0:
        collect_usr = Collection_User(user_id = user_id, 
                                      another_user_id = another_user_id,
                                      time = datetime.now())
                                      #用户user_id 收藏用户 another_user_id
        db_session.add(collect_usr)
        db_session.commit()
        update_collection_num(user_id,another_user_id,True)
    else:
        return "already"
    return "success"


def collection_special_author_cancel(user_id, author_id):
    another_user_id = author_id
    if (user_id == another_user_id):
        return "self"
    query = db_session.query(Collection_User).filter_by(user_id = user_id, another_user_id = another_user_id).all()
    if len(query) == 1:
        db_session.delete(query[0])
        db_session.commit()
        update_collection_num(user_id,another_user_id,False)
    else:
        return "already"
    return "success"

def create_user_collection(another_user_id,user_id):
    result=db_session.query(Collection_User).filter(and_(Collection_User.user_id==user_id,Collection_User.another_user_id==another_user_id)).all()
    if len(result)>0:
        pass
    else:
        collection=Collection_User(user_id=user_id,another_user_id=another_user_id,time=datetime.now())
        db_session.add(collection)
        db_session.commit()
        update_collection_num(user_id,another_user_id,True)


def delete_user_collection(another_user_id,user_id):
    db_session.query(Collection_User).filter(and_(Collection_User.user_id==user_id,Collection_User.another_user_id==another_user_id)).delete()
    db_session.commit()
    update_collection_num(user_id,another_user_id,False)

def update_collection_num(user_id,another_user_id,is_add):
    user=db_session.query(User).filter_by(user_id=user_id).scalar()
    another_user=db_session.query(User).filter_by(user_id=another_user_id).scalar()
    if is_add:
        user.follow_num+=1
        another_user.be_followed_num+=1
    else:
        user.follow_num-=1
        another_user.be_followed_num-=1     
    db_session.commit()

def collection_article(user_id,article_id):
    article=db_session.query(Article).filter_by(article_id=article_id).first()
    result=db_session.query(Collection_Article).filter(and_(Collection_Article.user_id==user_id,Collection_Article.article_id==article_id)).all()
    if article.user_id==user_id:
        return 'fail'
    elif len(result)>0:
        return 'already'
    else:
        collection_article=Collection_Article(user_id=user_id,article_id=article_id,time=datetime.now())
        db_session.add(collection_article)
        db_session.commit()
        return 'success'

def collection_activity(user_id,activity_id):
    result=db_session.query(Collection_Activity).filter(and_(Collection_Activity.activity_id==activity_id,Collection_Activity.user_id==user_id)).all()
    if len(result)>0:
        return 'already'
    else:
        collection_activity=Collection_Activity(user_id=user_id,activity_id=activity_id,time=datetime.now())
        db_session.add(collection_activity)
        db_session.commit()
        return 'success'

