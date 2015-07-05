# -*- coding: utf-8 -*-
from imports import *

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
	if article==None or not root_authorized():
		return 'fail'
	else:
		##先删除和这片文章相关的内容
		pretreamentment_article_delete(article_id)
		db_session.query(Article).filter_by(article_id=article_id).delete()
		db_session.commit()
		return 'success'
#######################################  删除一篇文章 end ########################################



#######################################  删除一条评论 start ########################################
def pretreamentment_comment_delete(comment_id):
	article=db_session.query(Article).join(Comment,Comment.article_id==Article.article_id).filter(Comment.comment_id==comment_id).first()
	update_comment_num(article.article_id,False)

def delete_comment_by_comment_id(comment_id,user_id):
	comment=db_session.query(Comment).filter_by(comment_id=comment_id).first()
	if (comment.user_id!=user_id and not root_authorized()) or comment==None:
		return 'fail'
	else:
		pretreamentment_comment_delete(comment_id)
		db_session.query(Comment).filter_by(comment_id=comment_id).delete()
		db_session.query(Comment).filter_by(reply_to_comment_id=comment_id).delete()
		db_session.commit()
		return 'success'
#######################################  删除一条评论 end ########################################



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

#######################################  删除一条接收到的评论 start ########################################
def pretreamentment_received_comment_delete(received_comment_id):
	article=db_session.query(Article).join(Comment,Comment.article_id==Article.article_id).filter(Comment.comment_id==received_comment_id).first()
	update_comment_num(article.article_id,False)

def delete_received_comment_by_comment_id(received_comment_id,user_id):
	comment=db_session.query(Comment).filter_by(comment_id=received_comment_id).first()
	if comment.to_user_id!=user_id or comment==None:
		return 'fail'
	else:
		pretreamentment_received_comment_delete(received_comment_id)
		db_session.query(Comment).filter_by(comment_id=received_comment_id).delete()
		db_session.commit()
		return 'success'
#######################################  删除一条接收到的评论 end ########################################

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
