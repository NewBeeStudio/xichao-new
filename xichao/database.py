# -*- coding: utf-8 -*-
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
