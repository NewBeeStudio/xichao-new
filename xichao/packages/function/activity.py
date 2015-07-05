# -*- coding: utf-8 -*-
from imports import *

def create_activity(title,content,title_image,activity_session_id,activity_time,abstract,place):
	result=db_session.query(Activity).filter_by(activity_session_id=activity_session_id).all()
	if len(result)>0:
		activity=db_session.query(Activity).filter_by(activity_session_id=activity_session_id).scalar()
		activity.name=title
		activity.content=content
		activity.picture=title_image
		activity.create_time=datetime.now()
		activity.activity_time=activity_time
		activity.abstract=abstract
		activity.place=place
		db_session.commit()
		return activity.activity_id
	else:
		activity=Activity(name=title,content=content,picture=title_image,create_time=datetime.now(),activity_session_id=activity_session_id,activity_time=activity_time,abstract=abstract,place=place)
		db_session.add(activity)
		db_session.commit()
		result=db_session.query(Activity).filter_by(activity_session_id=activity_session_id).first()
		return result.activity_id

def get_passed_activity_pagination(sort, page_id, perpage):
    if sort == 'time':
        query = db_session.query(Activity).order_by(Activity.activity_time.desc(), Activity.favor.desc())
    else:
        query = db_session.query(Activity).order_by(Activity.favor.desc(), Activity.activity_time.desc())
    return paginate(query = query, page = page_id, per_page = perpage, error_out = True)

def get_activity_information(activity_id):
	result=db_session.query(Activity).filter_by(activity_id=activity_id).all()
	if len(result)>0:
		return result[0]
	else:
		return None

def get_activity_comments(activity_id):
	result=db_session.query(Comment_activity,User.nick,User.photo).join(User,Comment_activity.user_id==User.user_id).filter(Comment_activity.activity_id==activity_id).order_by(desc(Comment_activity.time)).all()
	if len(result)>0:
		return result
	else:
		return None

def update_read_num_activity(activity_id):
	activity=db_session.query(Activity).filter_by(activity_id=activity_id).scalar()
	activity.read_num+=1
	db_session.commit()

###################################  评论函数  ####################################
def create_activity_comment(content,activity_id):
	user_id=int(session['user_id'])
	comment_activity=Comment_activity(activity_id=activity_id,content=content,user_id=user_id,time=datetime.now())
	db_session.add(comment_activity)
	db_session.commit()
def update_activity_comment_num(activity_id):
	activity=db_session.query(Activity).filter_by(activity_id=activity_id).scalar()
	activity.comment_num+=1
	db_session.commit()

