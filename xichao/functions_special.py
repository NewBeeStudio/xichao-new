# -*- coding: utf-8 -*-

from database import db_session
from models import User,Article,Special,Collection_Special,Collection_User
from functions import paginate

from sqlalchemy import  and_,or_
from flask import session
from datetime import datetime

##################################  专栏函数  ####################################
def get_all_specials(sort, page_id, perpage):
    if sort == 'time':
        query = db_session.query(Special).order_by(Special.last_modified.desc(), Special.coin.desc())
    else:
        query = db_session.query(Special).order_by(Special.coin.desc(), Special.last_modified.desc())
    return paginate(query = query, page = page_id, per_page = perpage, error_out = True)
    
def get_search_specials(search):
    query = db_session.query(Special).filter(Special.name.like('%'+search+'%')).order_by(Special.coin.desc())
    return paginate(query = query, page = 1, error_out = True)

def create_special_authorized():
	if 'user_id' in session:
		result = db_session.query(User).filter_by(user_id=int(session['user_id'])).all()[0]
		return result.role == 3
		## 专栏作家或者管理员
	else:
	    return False

def create_new_special(name, user_id, picture, introduction,
                        style, total_issue, update_frequency):
    special = Special(name = name, user_id = user_id,
                       picture = picture, introduction = introduction,
                       time = datetime.now(), style = style,
                       total_issue = total_issue,
                       update_frequency = update_frequency)
    db_session.add(special)
    user = db_session.query(User).filter_by(user_id = user_id).first();
    if user.role == 1:
        user.role = 2
    db_session.commit()
    return db_session.query(Special).filter_by(user_id = user_id, name = name).all()[0].special_id
    
def modify_special_func(name, user_id, picture, introduction,
                        style, total_issue, update_frequency):
    query = db_session.query(Special).filter_by(name = name, user_id = user_id).all()
    if (len(query) == 0):
        raise Exception
    special = query[0]
    special.picture = picture
    special.introduction = introduction
    special.style = style
    special.total_issue = total_issue
    special.update_frequency = update_frequency
    db_session.commit()
    return special.special_id
    
def get_userid_by_nick(nick):
    return db_session.query(User.user_id).filter_by(nick=nick).all()

def get_nick_by_userid(user_id):
    return db_session.query(User.nick).filter_by(user_id=user_id).all()[0][0]

def get_userid_from_session():
	if 'user_id' in session:
		result = db_session.query(User).filter_by(user_id=int(session['user_id'])).all()
		return result[0].user_id
	return 0

def get_special_author(userid):
    result = db_session.query(User).filter_by(user_id = userid).all()
    return result[0]

def get_special_information(special_id):
#	result=db_session.query(Special,User.nick).join(User).filter(Special.special_id==special_id).all()
    result = db_session.query(Special).filter_by(special_id = special_id).all()
    if len(result)>0:
        return result[0]
    else:
        return None
        
def get_special_collect_info(user_id, special_id):
    query = db_session.query(Collection_Special).filter_by(user_id = user_id, special_id = special_id).all()
    return len(query)
    
def get_author_collect_info(user_id, author_id):
    query = db_session.query(Collection_User).filter_by(user_id = user_id, another_user_id = author_id).all()
    return len(query)

def get_special_article(special_id, page_id, sort, per_page):
    if sort == "time":
#        print ddd
        query = db_session.query(Article).filter_by(special_id = special_id, is_draft = '0').order_by(Article.time.desc())
    else:
        query = db_session.query(Article).filter_by(special_id = special_id, is_draft = '0').order_by(Article.coins.desc())

    pagination = paginate(query = query, page = page_id, per_page = per_page, error_out = True)
    return pagination
    
def get_special_draft(special_id):
    return db_session.query(Article).filter_by(special_id = special_id, is_draft = '1').all()
    
def get_special_author_other(user_id, special_id, limit):
    query = db_session.query(Article.title, Article.article_id).filter(and_(Article.user_id == user_id, or_(Article.special_id == None, Article.special_id != special_id))).limit(limit).all()
    return query

def get_related_special(user_id):
    query = db_session.query(Special.special_id, Special.name, Special.picture, Special.favor, Special.coin, Special.user_id).join(Collection_Special).filter_by(user_id=user_id).limit(6).all()
    return query

def update_article_num_for_special(special_id,is_add):
	special=db_session.query(Special).filter_by(special_id=special_id).scalar()
	if is_add:
		special.article_num+=1
	else:
		special.article_num-=1
	db_session.commit()