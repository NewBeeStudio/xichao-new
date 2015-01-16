# -*- coding: utf-8 -*-
'''

	数据库基础模块

	定义db_session，用于和数据库进行交互
	定义Base类，作为父类，被子类继承，形成数据表类
	定义init_db函数，用于初始化数据表
'''
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DB_URL='mysql://root:@localhost/xichao?charset=utf8'
engine = create_engine(DB_URL, echo=True)

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


#建立数据库时一定要建立成utf8编码的，mysql的相应字符配置需要更改
def init_db():
    import models
    Base.metadata.create_all(bind=engine)
