# -*- coding: utf-8 -*-
'''
	
	数据模型模块

	定义了数据库的数据模型
'''

from sqlalchemy import Column, Integer, String, CHAR, SmallInteger, Date, DateTime
from database import Base


class User(Base):
	__tablename__ = 'user'
	__table_args__ = { 
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
        }   
	user_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, index=True)
	nick = Column(String(50), unique=True, nullable=False, index=True)
	gender=Column(CHAR(1), nullable=True)
	birthday=Column(Date, nullable=True)
	email = Column(String(60), unique=True,index=True,nullable=False)
	phone = Column(String(15), nullable=True)
	member_id = Column(String(6),unique=True,index=True,nullable=True)
	coin=Column(Integer,nullable=True)
	role=Column(SmallInteger,nullable=False)
	register_time=Column(DateTime,nullable=False)
	last_login_time=Column(DateTime,nullable=False)
	password=Column(String(60),nullable=False)
	#state=Column(CHAR(1),nullable=False)
	#photo=Column(String(255),nullable=True)

	def __init__(self, nick=None, email=None, role=None,register_time=None,last_login_time=None,password=None):
		self.nick = nick
		self.email = email
		self.role=role
		self.register_time=register_time
		self.last_login_time=last_login_time
		self.password=password

	def __repr__(self):
		return '<User %r>' % (self.nick)