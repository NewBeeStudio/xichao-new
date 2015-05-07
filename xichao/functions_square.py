# -*- coding: utf-8 -*-

from database import db_session
from models import HomePage,Article,User

from sqlalchemy import  and_, desc

#推荐语
def get_recommend_words():
	result=db_session.query(HomePage.recommend_words).first()
	return result

def get_article_group_by_coin(groups,category):
	result=db_session.query(Article,User.nick).join(User).filter(and_(Article.groups==groups,Article.category==category,Article.is_draft=='0')).order_by(desc(Article.coins)).limit(10).all()
	return result

def get_article_group_by_time(groups,category):
	result=db_session.query(Article,User.nick).join(User).filter(and_(Article.groups==groups,Article.category==category,Article.is_draft=='0')).order_by(desc(Article.time)).limit(10).all()
	return result
##拿9篇热门文章
def get_hot_ground_acticle():
	result=db_session.query(Article,User.nick).join(User).filter(and_(Article.groups=='1',Article.is_draft=='0')).order_by(desc(Article.coins)).limit(10).all()
	return result
##拿一篇推荐文章
def get_recommended_ground_article():
	result=db_session.query(Article).join(HomePage,HomePage.ground_recommended_article==Article.article_id).filter(and_(Article.groups=='1',Article.is_draft=='0')).first()
	return result