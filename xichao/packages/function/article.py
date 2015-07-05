# -*- coding: utf-8 -*-
from imports import *

###################################  获取文章摘要函数  ###############################
def get_abstract_plain_text(abstract):
	img_list=re.findall('<img.*?>',abstract)
	for img_r in img_list:
		abstract=abstract.replace(img_r,'')
	return abstract

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
	result=db_session.query(Article).filter_by(article_session_id=article_session_id).all()
	if (special_id != None) and (is_draft == '0'):
		special = db_session.query(Special).filter_by(special_id = special_id).scalar()
		special.last_modified = datetime.now()
		db_session.commit()

	if len(result)>0:
		article=db_session.query(Article).filter_by(article_session_id=article_session_id).scalar()
		article.title=title
		article.content=content
		article.picture=title_image
		article.time=datetime.now()
		article.is_draft=is_draft
		article.abstract=abstract
		article.book_id=book_id
		article.special_id=special_id
		article.category = category_id
		db_session.commit()
		return result[0].article_id
	else:
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

#返回1个元组，result[0][0]是Article类的数据库实例，result[0][1]是该Article实例所对应的User.nick,是字符串,result[0][2]是该Article实例所对应的Book实例
def get_article_information(article_id):
	result=db_session.query(Article,User,Book).join(User,Book).filter(Article.article_id==article_id).all()
	#print result[0]
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

def update_read_num(article_id):
	article=db_session.query(Article).filter_by(article_id=article_id).scalar()
	article.read_num+=1
	db_session.commit()

###################################  评论函数  ####################################
def create_comment(content,to_user_id,article_id,reply_to_comment_id):
	user_id=int(session['user_id'])
	comment=Comment(article_id=article_id,content=content,user_id=user_id,to_user_id=to_user_id,time=datetime.now(),reply_to_comment_id=reply_to_comment_id)
	db_session.add(comment)
	db_session.commit()
def update_comment_num(article_id,is_add):
	article=db_session.query(Article).filter_by(article_id=article_id).scalar()
	if is_add:
		article.comment_num+=1
	else:
		article.comment_num-=1
	db_session.commit()

###################################  获取文章组函数  #################################
def get_article_pagination_by_favor(group_id,category_id,page_id):
	query=db_session.query(Article,User.nick).join(User,User.user_id==Article.user_id).filter(and_(Article.groups==group_id,Article.category==category_id,Article.is_draft=='0')).order_by(desc(Article.coins))
	return paginate(query,page_id,10,False)
def get_article_pagination_by_time(group_id,category_id,page_id):
	query=db_session.query(Article,User.nick).join(User,User.user_id==Article.user_id).filter(and_(Article.groups==group_id,Article.category==category_id,Article.is_draft=='0')).order_by(desc(Article.time))
	return paginate(query,page_id,10,False)
