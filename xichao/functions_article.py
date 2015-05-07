# -*- coding: utf-8 -*-

from xichao import app
from database import db_session
from models import User,Article,Activity,Special,Book,Article_session,Activity_session,\
Comment,Comment_activity,Collection_Article,Collection_Special
from functions import paginate,update_comment_num
from functions_user import user_coin_add,user_coin_sub
from functions_special import special_coin_add

from sqlalchemy import  and_, desc
from datetime import datetime
import re
import shutil
import os


##################################  文章函数  ####################################
def get_article_session_id():
    article_session = Article_session()
    db_session.add(article_session)
    db_session.commit()
    result=db_session.query(Article_session.article_session_id).order_by(desc(Article_session.article_session_id)).first()
    return result[0]
def get_activity_session_id():
	activity_session=Activity_session()
	db_session.add(activity_session)
	db_session.commit()
	result=db_session.query(Activity_session.activity_session_id).order_by(desc(Activity_session.activity_session_id)).first()
	return result[0]

#添加文章
def create_article(title,content,title_image,article_session_id,is_draft,user_id,group_id,category_id,abstract,book_id,special_id=None):
	print "#############\n\n\n\n\n\@@@@@@@@@@@@@@@@@@"
	result=db_session.query(Article).filter_by(article_session_id=article_session_id).all()
	if (special_id != None) and (is_draft == '0'):
		special = db_session.query(Special).filter_by(special_id = special_id).scalar()
		special.last_modified = datetime.now()
		db_session.commit()

	if len(result)>0:
		print "#############\n\n\n\n\n\################"
		article=db_session.query(Article).filter_by(article_session_id=article_session_id).scalar()
		article.title=title
		article.content=content
		article.picture=title_image
		article.time=datetime.now()
		article.is_draft=is_draft
		article.abstract=abstract
		article.book_id=book_id
		article.special_id=special_id
		db_session.commit()
		return result[0].article_id
	else:
		print "#############\n\n\n\n\n\@@@@@@@@@@@@@@@@@@"
		article=Article(title=title,content=content,picture=title_image,time=datetime.now(),user_id=user_id,article_session_id=article_session_id,is_draft=is_draft,groups=group_id,category=category_id,abstract=abstract,book_id=book_id,special_id=special_id)
		db_session.add(article)
		db_session.commit()
		result=db_session.query(Article).filter_by(article_session_id=article_session_id).first()
		return result.article_id
	

def create_book(book_picture,book_author,book_press,book_page_num,book_price,book_press_time,book_title,book_ISBN,book_binding):
	result=db_session.query(Book).filter_by(ISBN=book_ISBN).all()
	if len(result)>0:
		book=db_session.query(Book).filter_by(ISBN=book_ISBN).scalar()
		book.favor+=1
		db_session.commit()
		return result[0].book_id
	else:
		book=Book(title=book_title,ISBN=book_ISBN,picture=book_picture,author=book_author,press=book_press,page_num=book_page_num,price=book_price,press_time=book_press_time,binding=book_binding)
		db_session.add(book)
		db_session.commit()
		result=db_session.query(Book).filter_by(ISBN=book_ISBN).first()
		return result.book_id

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


def get_user_id(nick):
	user_id=db_session.query(User.user_id).filter_by(nick=nick).first()
	return user_id[0]


#返回1个元组，result[0][0]是Article类的数据库实例，result[0][1]是该Article实例所对应的User.nick,是字符串,result[0][2]是该Article实例所对应的Book实例
def get_article_information(article_id):
	result=db_session.query(Article,User,Book).join(User,Book).filter(Article.article_id==article_id).all()
	#print result[0]
	if len(result)>0:
		return result[0]
	else:
		return None

def get_activity_information(activity_id):
	result=db_session.query(Activity).filter_by(activity_id=activity_id).all()
	if len(result)>0:
		return result[0]
	else:
		return None

#返回一个列表，列表中的元素为元组，result[x][0]是Comment类的数据库实例，result[x][1]是该Comment所对应的用户昵称,result[x][2]是该Comment所对应的用户头像,result[x][3]是该Comment所对应的用户id
def get_article_comments(article_id):
	result=db_session.query(Comment,User.nick,User.photo,User.user_id).join(User,Comment.user_id==User.user_id).filter(Comment.article_id==article_id).order_by(desc(Comment.time)).all()
	if len(result)>0:
		return result
	else:
		return None
def get_article_comments_pagination(article_id,page_id,perpage):
	query=db_session.query(Comment,User.nick,User.photo,User.user_id).join(User,Comment.user_id==User.user_id).filter(and_(Comment.article_id==article_id,Comment.reply_to_comment_id==0)).order_by(desc(Comment.time))
	return paginate(query = query, page = page_id, per_page = perpage, error_out = True)
	#root_comment_reply=
def get_comment_reply(article_id,comment_id):
	result=db_session.query(Comment,User.nick,User.photo,User.user_id).join(User,Comment.user_id==User.user_id).filter(and_(Comment.article_id==article_id,Comment.reply_to_comment_id==comment_id)).order_by(Comment.time).all()
	return  result

def get_current_comment_id():
	result=db_session.query(Comment).order_by(desc(Comment.comment_id)).all()
	return result[0].comment_id
	
def get_activity_comments(activity_id):
	result=db_session.query(Comment_activity,User.nick,User.photo).join(User,Comment_activity.user_id==User.user_id).filter(Comment_activity.activity_id==activity_id).order_by(desc(Comment_activity.time)).all()
	if len(result)>0:
		return result
	else:
		return None

def update_read_num(article_id):
	article=db_session.query(Article).filter_by(article_id=article_id).scalar()
	article.read_num+=1
	db_session.commit()


def update_read_num_activity(activity_id):
	activity=db_session.query(Activity).filter_by(activity_id=activity_id).scalar()
	activity.read_num+=1
	db_session.commit()
	
###################################  获取文章摘要函数  ###############################
def get_abstract_plain_text(abstract):
	img_list=re.findall('<img.*?>',abstract)
	for img_r in img_list:
		abstract=abstract.replace(img_r,'')
	return abstract

def article_coin_add(article_id,num):
	article=db_session.query(Article).filter_by(article_id=article_id).scalar()
	article.coins+=num
	if (article.groups =='3'):
	    special_coin_add(article.special_id, num)
	db_session.commit()
	article=db_session.query(Article).filter_by(article_id=article_id).first()
	user_coin_add(user_id=article.user_id,num=num)

def process_article_award(user_id,article_id,award_num):
	article=db_session.query(Article).filter_by(article_id=article_id).first()
	if article.user_id==user_id:
		return 'fail'
	else:
		user_coin_sub(user_id=user_id,num=award_num)
		article_coin_add(article_id=article_id,num=award_num)
		return 'success'

def examine_article_id(article_id):
	result=db_session.query(Article).filter_by(article_id=article_id).all()
	if len(result)>0:
		return True
	else:
		return False



#######################################  删除一条评论 start ########################################
def pretreamentment_comment_delete(comment_id):
	article=db_session.query(Article).join(Comment,Comment.article_id==Article.article_id).filter(Comment.comment_id==comment_id).first()
	update_comment_num(article.article_id,False)

def delete_comment_by_comment_id(comment_id,user_id):
	comment=db_session.query(Comment).filter_by(comment_id=comment_id).first()
	if comment.user_id!=user_id or comment==None:
		return 'fail'
	else:
		pretreamentment_comment_delete(comment_id)
		db_session.query(Comment).filter_by(comment_id=comment_id).delete()
		db_session.query(Comment).filter_by(reply_to_comment_id=comment_id).delete()
		db_session.commit()
		return 'success'
#######################################  删除一条评论 end ########################################

def update_article_favor(article_id,is_add):
	article=db_session.query(Article).filter_by(article_id=article_id).scalar()
	if is_add:
		article.favor+=1
	else:
		article.favor-=1
	db_session.commit()

#######################################  删除一条文章收藏 start ########################################
def pretreamentment_collection_article_delete(collection_article_id):
	article=db_session.query(Article).join(Collection_Article,Collection_Article.article_id==Article.article_id).filter(Collection_Article.collection_article_id==collection_article_id).first()
	update_article_favor(article.article_id,False)

def delete_collection_article_by_collection_article_id(collection_article_id,user_id):
	collection_article=db_session.query(Collection_Article).filter_by(collection_article_id=collection_article_id).first()
	if collection_article.user_id!=user_id or collection_article==None:
		return 'fail'
	else:
		pretreamentment_collection_article_delete(collection_article_id)
		db_session.query(Collection_Article).filter_by(collection_article_id=collection_article_id).delete()
		db_session.commit()
		return 'success'
#######################################  删除一条文章收藏 end ########################################

#######################################  删除一篇文章 start ########################################
##删除文章的内容文件夹
def delete_article_content_folder(article_session_id):
	try:
		shutil.rmtree(os.path.join(app.config['ARTICLE_CONTENT_DEST'], str(article_session_id)))
	except:
		pass
##删除文章的题图
def delete_article_title_image(picture):
	picture_path_list=picture.split('/')
	picture_path_list_length=len(picture_path_list)
	title_image=picture_path_list[picture_path_list_length-1]
	if title_image in app.config['DEFAULT_ARTICLE_TITLT_IMAGE']:
		pass
	else:
		try:
			os.remove(os.path.join(app.config['ARTICLE_TITLE_DEST'],title_image))
		except:
			pass
		
##删除文章的评论
def delete_comments_by_article_id(article_id):
	db_session.query(Comment).filter(Comment.article_id==article_id).delete()
	db_session.commit()
##删除对文章的收藏
def delete_collection_article_by_article_id(article_id):
	db_session.query(Collection_Article).filter(Collection_Article.article_id==article_id).delete()
	db_session.commit()
##先删除和这片文章相关的内容
def pretreamentment_article_delete(article_id):
	article=db_session.query(Article).filter_by(article_id=article_id).first()
	##删除内容文件夹
	delete_article_content_folder(article.article_session_id)
	##删除题图
	delete_article_title_image(article.picture)
	##删除评论
	delete_comments_by_article_id(article_id)
	##删除对该文章的收藏
	delete_collection_article_by_article_id(article_id)
def delete_article_by_article_id(article_id,user_id):
	article=db_session.query(Article).filter_by(article_id=article_id).first()
	if article==None or article.user_id!=user_id:
		return 'fail'
	else:
		##先删除和这片文章相关的内容
		pretreamentment_article_delete(article_id)
		db_session.query(Article).filter_by(article_id=article_id).delete()
		db_session.commit()
		return 'success'
#######################################  删除一篇文章 end ########################################

#######################################  删除一个专栏 start ########################################

def delete_collection_special_by_special_id(special_id):
	db_session.query(Collection_Special).filter(Collection_Special.special_id==special_id).delete()
	db_session.commit()

def delete_articles_by_special_id(special_id):
	articles=db_session.query(Article).filter(Article.special_id==special_id).all()
	if articles==None:
		pass
	else:
		for article in articles:
			delete_article_by_article_id(article.article_id)

def pretreamentment_special_delete(special_id):
	delete_collection_special_by_special_id(special_id)
	delete_articles_by_special_id(special_id)

def delete_special_by_special_id(special_id,user_id):
	special=db_session.query(Special).filter(Special.special_id==special_id).first()
	if special.user_id!=user_id or special==None:
		return 'fail'
	else:
		pretreamentment_special_delete(special_id)
		db_session.query(Special).filter_by(special_id=special_id).delete()
		db_session.commit()
		return 'success'
#######################################  删除一个专栏 end ########################################