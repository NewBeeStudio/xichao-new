# -*- coding: utf-8 -*-
from imports import *

##################################  首页函数  ####################################
def get_homepage_specials():
    query = db_session.query(HomePage).all()[0]
    special1 = db_session.query(Special).filter_by(special_id = query.special1).all()[0]
    special2 = db_session.query(Special).filter_by(special_id = query.special2).all()[0]
    special3 = db_session.query(Special).filter_by(special_id = query.special3).all()[0]
    special4 = db_session.query(Special).filter_by(special_id = query.special4).all()[0]
    return [special1, special2, special3, special4], [query.special1_image, query.special2_image, query.special3_image, query.special4_image]
    
def get_hot_articles(num):
    query = db_session.query(Article).filter_by(is_draft = '0').order_by(Article.coins.desc()).limit(10).all()
    return query
    
def get_all_special():
    query = db_session.query(Special).order_by(Special.coin.desc()).all()
    return query

def get_all_focus_article(limit):
	if 'user_id' in session:
		userid = int(session['user_id'])
		query1 = db_session.query(Article).join(Collection_Special, Collection_Special.special_id == Article.special_id).filter(and_(Collection_Special.user_id == userid, Article.is_draft == '0'))
		query2 = db_session.query(Article).join(Collection_User, Collection_User.another_user_id == Article.user_id).filter(and_(Collection_User.user_id == userid, Article.is_draft == '0'))
		return query1.union(query2).order_by(Article.time.desc()).limit(limit).all();
	else:
		return []

def get_latest_articles(limit):
	query = db_session.query(Article).filter_by(is_draft = '0').order_by(Article.time.desc()).limit(limit).all()
	return query

def modify_homepage_func(special1, url1,
                         special2, url2,
                         special3, url3,
                         special4, url4,
                         recommend_actctivity):
    
    special1 = db_session.query(Special).filter_by(name = special1).all()
    if (len(special1) == 0):
        return '1'
    special2 = db_session.query(Special).filter_by(name = special2).all()
    if (len(special2) == 0):
        return '2'
    special3 = db_session.query(Special).filter_by(name = special3).all()
    if (len(special3) == 0):
        return '3'
    special4 = db_session.query(Special).filter_by(name = special4).all()
    if (len(special4) == 0):
        return '4'

    special1 = special1[0].special_id
    special2 = special2[0].special_id
    special3 = special3[0].special_id
    special4 = special4[0].special_id
    
    query = db_session.query(HomePage).all()[0]
    query.special1 = special1
    query.special2 = special2
    query.special3 = special3
    query.special4 = special4

    if url1 != '':
        query.special1_image = url1
    if url2 != '':
        query.special2_image = url2
    if url3 != '':
        query.special3_image = url3
    if url4 != '':
        query.special4_image = url4

    query.recommended_activity = recommend_actctivity

    db_session.commit()
    return 'success'

def get_hot_ground_acticle():
    result=db_session.query(Article,User.nick).join(User).filter(and_(Article.groups=='1',Article.is_draft=='0')).order_by(desc(Article.coins)).limit(10).all()
    return result

def get_recommended_ground_article():
    result=db_session.query(Article).join(HomePage,HomePage.ground_recommended_article==Article.article_id).filter(and_(Article.groups=='1',Article.is_draft=='0')).first()
    return result

def get_most_hot_ground_article():
    result=db_session.query(Article,User.nick).join(User).filter(and_(Article.groups=='1',Article.is_draft=='0')).order_by(desc(Article.coins)).first()
    return result

def get_most_hot_activity():
    act_id = db_session.query(HomePage).first().recommended_activity;
    result=db_session.query(Activity).filter_by(activity_id = act_id).first()
    return result

def get_article_group_by_coin(groups,category):
    result=db_session.query(Article,User.nick).join(User).filter(and_(Article.groups==groups,Article.category==category,Article.is_draft=='0')).order_by(desc(Article.coins)).limit(10).all()
    return result

def get_article_group_by_time(groups,category):
    result=db_session.query(Article,User.nick).join(User).filter(and_(Article.groups==groups,Article.category==category,Article.is_draft=='0')).order_by(desc(Article.time)).limit(10).all()
    return result

def has_collected(user_id,another_user_id):
    result=db_session.query(Collection_User).filter(and_(Collection_User.user_id==user_id,Collection_User.another_user_id==another_user_id)).all()
    if len(result)>0:
        return 'yes'
    else:
        return 'no'