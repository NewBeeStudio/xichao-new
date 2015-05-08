# -*- coding: utf-8 -*-
'''

	功能函数模块

	实现一些数据库基本的功能，被高层次代码所调用

'''
from xichao import app
from models import User,Article,Special,Comment,\
Activity,Collection_Special,Collection_User,\
Collection_Article,Collection_Activity,HomePage
from database import db_session
from flask import abort
from sqlalchemy import and_, desc
from flask.ext.sqlalchemy import Pagination
import os
import models
import urllib
import json




###################################  分页函数  ######################################
##源自官方的实现
def paginate(query,page,per_page=20,error_out=True):
	if error_out and page < 1:
		abort(404)
	items = query.limit(per_page).offset((page - 1) * per_page).all()
	if not items and page != 1 and error_out:
		abort(404)
	if page == 1 and len(items) < per_page:
		total = len(items)
	else:
		total = query.order_by(None).count()
	return Pagination(query, page, per_page, total, items)



###################################  获取文章组函数  #################################
def get_article_pagination_by_favor(group_id,category_id,page_id):
	query=db_session.query(Article,User.nick).join(User,User.user_id==Article.user_id).filter(and_(Article.groups==group_id,Article.category==category_id,Article.is_draft=='0')).order_by(desc(Article.coins))
	return paginate(query,page_id,10,False)

def get_article_pagination_by_time(group_id,category_id,page_id):
	query=db_session.query(Article,User.nick).join(User,User.user_id==Article.user_id).filter(and_(Article.groups==group_id,Article.category==category_id,Article.is_draft=='0')).order_by(desc(Article.time))
	return paginate(query,page_id,10,False)

def get_most_hot_ground_article():
	result=db_session.query(Article,User.nick).join(User).filter(and_(Article.groups=='1',Article.is_draft=='0')).order_by(desc(Article.coins)).first()
	return result

def get_most_hot_activity():
	act_id = db_session.query(HomePage).first().recommended_activity;
	result=db_session.query(Activity).filter_by(activity_id = act_id).first()
	return result

def update_activity_favor(activity_id,is_add):
	activity=db_session.query(Activity).filter_by(activity_id=activity_id).scalar()
	if is_add:
		activity.favor+=1
	else:
		activity.favor-=1
	db_session.commit()

def get_current_activity_list(time):
	result=db_session.query(Activity).filter(Activity.activity_time>time).all()
	return result

def get_passed_activity_list(time):
	result=db_session.query(Activity).filter(Activity.activity_time<time).order_by(desc(Activity.activity_time)).limit(4).all()
	return result

def get_follow_num(user_id):
	result=db_session.query(Collection_User).filter_by(user_id=user_id).all()
	return len(result)

def get_be_followed_num(user_id):
	result=db_session.query(Collection_User).filter_by(another_user_id=user_id).all()
	return len(result)


def get_article_pagination_by_user_id(user_id,by_time,page_id):
	if by_time:
		query=db_session.query(Article).filter(and_(Article.user_id==user_id,Article.is_draft=='0',Article.special_id==None)).order_by(desc(Article.time))
	else:
		query=db_session.query(Article).filter(and_(Article.user_id==user_id,Article.is_draft=='0',Article.special_id==None)).order_by(desc(Article.coins))
	return paginate(query,page_id,5,False)

def get_collection_author_list(user_id):
	result=db_session.query(User).join(Collection_User,Collection_User.another_user_id==User.user_id).filter(Collection_User.user_id==user_id).all()
	return result

def get_comment_pagination_by_user_id(user_id,page_id):
	query=db_session.query(Comment,Article).join(Article).filter(Comment.user_id==user_id).order_by(desc(Comment.time))
	return paginate(query,page_id,4,False)

def get_article_draft_pagination(user_id,page_id):
	query=db_session.query(Article).filter(and_(Article.user_id==user_id,Article.is_draft=='1'))
	return paginate(query,page_id,5,False)

def get_article_collection_pagination(user_id,page_id):
	query=db_session.query(Article,Collection_Article,User).join(Collection_Article,Collection_Article.article_id==Article.article_id).join(User,User.user_id==Article.user_id).filter(Collection_Article.user_id==user_id)
	return paginate(query,page_id,5,False)

def get_activity_collection_pagination(user_id,page_id):
	query=db_session.query(Activity,Collection_Activity).join(Collection_Activity,Collection_Activity.activity_id==Activity.activity_id).filter(Collection_Activity.user_id==user_id)
	return paginate(query,page_id,5,False)

def get_user_collection_pagination(user_id,page_id):
	query=db_session.query(User,Collection_User).join(Collection_User,Collection_User.another_user_id==User.user_id).filter(Collection_User.user_id==user_id)
	return paginate(query,page_id,10,False)

def get_special_collection_pagination(user_id,page_id):
	query=db_session.query(Special,Collection_Special).join(Collection_Special,Collection_Special.special_id==Special.special_id).filter(Collection_Special.user_id==user_id)
	return paginate(query,page_id,10,False)

def get_fans_pagination(user_id,page_id):
	query=db_session.query(User).join(Collection_User,Collection_User.user_id==User.user_id).filter(Collection_User.another_user_id==user_id)
	return paginate(query,page_id,10,False)

##目前来说，3是管理员
def get_message_pagination(user_id,page_id):
	query=db_session.query(models.Message,User).join(User,User.user_id==models.Message.user_id).filter(and_(models.Message.to_user_id==user_id,User.role!=3)).order_by(desc(models.Message.time))
	return paginate(query,page_id,4,False)

def get_received_comment_pagination(user_id,page_id):
	query=db_session.query(Comment,User,Article).join(User,User.user_id==Comment.user_id).join(Article,Article.article_id==Comment.article_id).filter(Comment.to_user_id==user_id).order_by(desc(Comment.time))
	return paginate(query,page_id,4,False)
##目前来说，3是管理员
def get_notification_pagination(user_id,page_id):
	query=db_session.query(models.Message).join(User,User.user_id==models.Message.user_id).filter(and_(models.Message.to_user_id==user_id,User.role==3)).order_by(desc(models.Message.time))
	return paginate(query,page_id,4,False)

def get_special_pagination(user_id,page_id):
	query=db_session.query(Special).filter(Special.user_id==user_id)
	return paginate(query,page_id,3,False)

def get_has_prev(pagination):
	if pagination.has_prev:
		return 'yes'
	else:
		return 'no'
def get_has_next(pagination):
	if pagination.has_next:
		return 'yes'
	else:
		return 'no'


## changed here!
def update_user_basic_information_by_user_id(user_id,nick,gender,birthday,phone):
	user=db_session.query(User).filter_by(user_id=user_id).scalar()
	user.nick=nick
	user.gender=gender
	user.birthday=birthday
	user.phone=phone
	db_session.commit()
	##删除原先的头像
	if birthday==None and phone!=None:
		return 'success_no_birthday'
	elif birthday!=None and phone==None:
		return 'success_no_phone'
	elif birthday==None and phone==None:
		return 'success_no_birthday_phone'
	else:
		return 'success'

def delete(file_path):
	file_path_list=file_path.split('/')
	file_path_list_length=len(file_path_list)
	filename=file_path_list[file_path_list_length-1]
	if filename in app.config['DEFAULT_FILE']:
		pass
	else:
		try:
			os.remove(os.path.join(os.path.dirname(__file__),file_path[1:]))
			print 'delete file success'
		except Exception,e:
			print 'delete file fail'
			print e

def update_user_avatar(user_id,avatar):
	user=db_session.query(User).filter_by(user_id=user_id).scalar()
	old_avatar=user.photo
	user.photo=avatar
	db_session.commit()
	delete(old_avatar)
	return 'success'

def update_user_cover(user_id,cover):
	user=db_session.query(User).filter_by(user_id=user_id).scalar()
	old_cover=user.cover
	user.cover=cover
	db_session.commit()
	delete(old_cover)
	return 'success'

def update_user_slogon(user_id,slogon):
	user=db_session.query(User).filter_by(user_id=user_id).scalar()
	user.slogon=slogon
	db_session.commit()
	return 'success'

def update_member_id(user_id,member_id):
	user=db_session.query(User).filter_by(user_id=user_id).scalar()
	user.member_id=member_id
	try:
		db_session.commit()
		return 'success'
	except:
		return 'fail'









#######################################  删除一条活动收藏 start ########################################
def pretreamentment_collection_artivity_delete(collection_activity_id):
	activity=db_session.query(Activity).join(Collection_Activity,Collection_Activity.activity_id==Activity.activity_id).filter(Collection_Activity.collection_activity_id==collection_activity_id).first()
	update_activity_favor(activity.activity_id,False)

def delete_collection_activity_by_activity_id(collection_activity_id,user_id):
	collection_activity=db_session.query(Collection_Activity).filter_by(collection_activity_id=collection_activity_id).first()
	if collection_activity.user_id!=user_id or collection_activity==None:
		return 'fail'
	else:
		pretreamentment_collection_artivity_delete(collection_activity_id)
		db_session.query(Collection_Activity).filter_by(collection_activity_id=collection_activity_id).delete()
		db_session.commit()
		##更新相关信息
		return 'success'
#######################################  删除一条活动收藏 end ########################################




#######################################  删除一条私信 start ########################################
def pretreamentment_message_delete(message_id):
	pass
def delete_message_by_message_id(message_id,user_id):
	message=db_session.query(models.Message).filter(models.Message.message_id==message_id).first()
	if message.to_user_id!=user_id or message==None:
		return 'fail'
	else:
		pretreamentment_message_delete(message_id)
		db_session.query(models.Message).filter(models.Message.message_id==message_id).delete()
		db_session.commit()
		return 'success'
#######################################  删除一条私信 end ########################################


	


#######################################  获取发表的文章数目 start ########################################

def get_article_number(user_id):
	result=db_session.query(Article).filter(and_(Article.user_id==user_id,Article.is_draft=='0',Article.groups!='3')).all()
	return len(result)

#######################################  获取发表的文章数目 end ########################################

#######################################  获取消息数目 start ########################################
def get_message_number(user_id):
	result=db_session.query(models.Message).join(User,User.user_id==models.Message.user_id).filter(and_(models.Message.to_user_id==user_id,models.Message.is_read=='0',User.role!=3)).all()
	return len(result)
def get_comment_number(user_id):
	result=db_session.query(Comment).filter(and_(Comment.to_user_id==user_id,Comment.is_read=='0')).all()
	return len(result)
def get_notification_number(user_id):
	result=db_session.query(models.Message).join(User,User.user_id==models.Message.user_id).filter(and_(models.Message.to_user_id==user_id,models.Message.is_read=='0',User.role==3)).all()
	return len(result)
#######################################  获取消息数目 end ########################################

#######################################  更新消息阅读状态 start ########################################
def update_message_read_state_by_message_id(message_id):
	db_session.query(models.Message).filter(models.Message.message_id==message_id).update({'is_read':'1'})
	db_session.commit()

def update_comment_read_state_by_comment_id(comment_id):
	db_session.query(Comment).filter(Comment.comment_id==comment_id).update({'is_read':'1'})
	db_session.commit()

def update_notification_read_state_by_notification_id(notification_id):
	update_message_read_state_by_message_id(notification_id)


def update_message_read_state(message_pagination):
	for item in message_pagination.items:
		update_message_read_state_by_message_id(item[0].message_id)
def update_comment_read_state(comment_pagination):
	for item in comment_pagination.items:
		update_comment_read_state_by_comment_id(item[0].comment_id)
def update_notification_read_state(notification_pagination):
	for item in notification_pagination.items:
		update_notification_read_state_by_notification_id(item.message_id)
#######################################  更新消息阅读状态 end ########################################




def get_point_by_member_id(member_id):
    try:
        member_data = urllib.urlopen('http://shjdxcsd.xicp.net:4057/website_read.aspx?Secret=18A6E54B00574FD5C172C52C3D689C8E&CardID='+member_id).read()
        member_data =  member_data.split('}')[0]+'}'
        memberDB = json.loads(member_data)
    except:
        return 0
    try:
        point=int(memberDB["coin"])
    except:
        return 0
    return point

##COMMON

def update_comment_num(article_id,is_add):
	article=db_session.query(Article).filter_by(article_id=article_id).scalar()
	if is_add:
		article.comment_num+=1
	else:
		article.comment_num-=1
	db_session.commit()