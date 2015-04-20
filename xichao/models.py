# -*- coding: utf-8 -*-
'''
    
    数据模型模块

    定义了数据库的数据模型
'''

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy import String, CHAR, Text, SmallInteger, Date, DateTime
from database import Base

from flask.ext.login import UserMixin
from xichao import login_serializer
from hashlib import md5
import datetime
import decimal

## 格式: Column(type, nullable, unique, index)


class AutoSerialize(object):
    '''
    Mixin for retrieving public fields of model in json-compatible format
    '''
    __allowed_in_json__ = None

    def get_serialize(self, exclude=()):
        '''Returns model's PUBLIC data for jsonify'''
        data = {}
        keys = self._sa_class_manager.mapper.mapped_table.columns
        public = self.__allowed_in_json__
        for col in keys:
            if public is not None:
                if col.name not in public:
                    continue
            if col.name in exclude:
                continue
            data[col.name] = self._serialize(getattr(self, col.name))
        return data

    @classmethod
    def _serialize(cls, value):
        if type(value) in (int, float, long, bool):
            ret = str(value)
        elif type(value) is unicode:
            ret = value.encode('utf-8')
        elif isinstance(value, datetime.date):
            ret = value.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(value, datetime.time) or isinstance(value, datetime.datetime):
            ret = value.isoformat()
        elif isinstance(value, decimal.Decimal):
            ret = str(value)
        else:
            ret = value

        return ret


##################################  首页模型  ####################################

class HomePage(Base, AutoSerialize):
    __tablename__ = 'homepage'
    __table_args__ = { 
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }

    ########## Primary索引 ##########
    homepage_id = Column(Integer, primary_key=True, autoincrement=True, 
                                  nullable=False, index=True)

    ########## 普通列 ##########
    special1 = Column(Integer, nullable = False, index = True)
    special2 = Column(Integer, nullable = False, index = True)
    special3 = Column(Integer, nullable = False, index = True)
    special4 = Column(Integer, nullable = False, index = True)
    
    special1_image = Column(String(255), nullable = False)
    special2_image = Column(String(255), nullable = False)
    special3_image = Column(String(255), nullable = False)
    special4_image = Column(String(255), nullable = False)

    ground_recommended_article=Column(Integer,nullable=False,default=1)

    
    ########## Index/Unique索引 ##########
    def __init__(self, special1=1, special2=2, special3=3, special4=4):
        self.special1 = special1
        self.special2 = special2
        self.special3 = special3
        self.special4 = special4
        
        self.special1_image = u'/upload/homepage/square-120150221154956.jpg'
        self.special2_image = u'/upload/homepage/square-220150221155006.jpg'
        self.special3_image = u'/upload/homepage/square-320150221155013.jpg'
        self.special4_image = u'/upload/homepage/square-120150221155023.jpg'

    def __repr__(self):
        return '<HomePage %r %r %r %r>' % (self.special1, self.special2, self.special3, self.special4)


##################################  用户模型  ####################################

class User(Base, UserMixin, AutoSerialize):
    __tablename__ = 'user'
    __table_args__ = { 
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }
    __allowed_in_json__ = ['nick','user_id','photo']

    ########## Primary索引 ##########
    user_id = Column(Integer, primary_key=True, autoincrement=True, 
                              nullable=False, index=True)

    ########## 普通列 ##########
    gender = Column(CHAR(1), nullable = True)
    birthday = Column(Date, nullable = True)
    phone = Column(String(15), nullable = True)
    coin = Column(Integer, nullable = False, default=0)
    role = Column(SmallInteger, nullable = False, default = 1)
    register_time = Column(DateTime, nullable = False)
    last_login_time = Column(DateTime, nullable = False)
    password = Column(String(60), nullable = False)
    state = Column(CHAR(1), nullable = False)
    photo = Column(String(255), nullable = True)
    slogon = Column(String(255), nullable = False)

    follow_num=Column(Integer,nullable=False,default=0)
    be_followed_num=Column(Integer,nullable=False,default=0)
    ########## Index/Unique索引 ##########
    nick = Column(String(60), nullable = False, 
                              unique = True, index = True)
    email = Column(String(60), nullable = False, 
                              unique = True, index = True)
    member_id = Column(String(15), nullable = True, 
                              unique = True, index = True)

    def __init__(self, nick = None, email = None, 
                       role = None, register_time = None,
                       last_login_time = None, password = None,
                       state = None,photo=None,slogon=None):
        self.nick = nick
        self.email = email
        self.role = role
        self.register_time = register_time
        self.last_login_time = last_login_time
        self.password = password
        self.state = state
        self.photo=photo
        self.slogon=slogon

    def __repr__(self):
        return '<User %r>' % (self.nick)

    #override
    def get_id(self):
        return unicode(self.user_id)

    #override, 产生cookie token
    def get_auth_token(self):
        data = (self.user_id, md5(self.password).hexdigest())
        return login_serializer.dumps(data)
        

##################################  书籍模型  ####################################

class Book(Base,AutoSerialize):
    __tablename__ = 'book'
    __table_args__ = { 
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }

    ########## Primary索引 ##########
    book_id = Column(Integer, primary_key=True, autoincrement=True, 
                              nullable=False, index=True)

    ########## 普通列 ##########
    picture = Column(String(255), nullable = False)
    author = Column(String(255), nullable = False)
    press = Column(String(50), nullable = False)
    page_num = Column(String(5), nullable = False)
    price = Column(String(10), nullable = False)
    press_time = Column(String(50),nullable=False)
    binding=Column(String(10),nullable=False)
    #被关联的次数
    favor=Column(Integer,nullable=False,index=True,default=1)
    ########## Index/Unique索引 ##########
    title = Column(String(50), nullable = False, 
                   unique = False, index = True)
    ISBN = Column(String(50), nullable = False,
                   unique = True, index = True)

    def __init__(self, title = None, ISBN = None,
                       picture = None, author = None,
                       press = None, page_num = None,
                       price = None, press_time=None,binding=None):
        self.title = title
        self.ISBN = ISBN
        self.picture = picture
        self.author = author
        self.press = press
        self.page_num = page_num
        self.price = price
        self.press_time=press_time
        self.binding=binding

    def __repr__(self):
        return '<Book %r>' % (self.title)


##################################  专栏模型  ####################################

class Special(Base,AutoSerialize):
    __tablename__ = 'special'
    __table_args__ = { 
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }
    __allowed_in_json__ = ['name','special_id','picture','article_num','coin','favor']
    ########## Primary索引 ##########
    special_id = Column(Integer, primary_key=True, autoincrement=True, 
                                 nullable=False, index=True)

    ########## 普通列 ##########
    name = Column(String(40), nullable = False)
    picture = Column(String(255), nullable = False)
    introduction = Column(String(600), nullable = False)
    article_num = Column(Integer, nullable = False, default = 0)
    time = Column(DateTime, nullable = False)

        ########## Added ##########
    total_issue = Column(String(40), nullable = False, default = "未知")
    update_frequency = Column(String(40), nullable = False, default = "未知")
    style = Column(String(40), nullable = False, default = "测试专栏")

    ########## Index/Unique索引 ##########
    favor = Column(Integer, nullable = False, 
                   unique = False, index = True, default = 0)
    coin = Column(Integer, nullable = False, unique=False, index=True,default=0)
    last_modified = Column(DateTime, nullable = False)

    ########## Foreign Key ##########
    user_id = Column(Integer, ForeignKey('user.user_id'), index=True)

    def __init__(self, name = None, user_id = None,
                       picture = None, introduction = None,
                       time = None, style = None,
                       total_issue = None,
                       update_frequency = None):
        self.name = name
        self.picture = picture
        self.introduction = introduction
        self.article_num = 0
        self.time = time
        self.favor = 0
        self.last_modified = time
        self.user_id = user_id
        self.style = style
        self.total_issue = total_issue
        self.update_frequency = update_frequency

    def __repr__(self):
        return '<Special %r>' % (self.name)


##################################  文章模型  ####################################

class Article(Base,AutoSerialize):
    __tablename__ = 'article'
    __table_args__ = { 
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }
    __allowed_in_json__ = ['title','article_id','picture','time','comment_num','coins']
    ########## Primary索引 ##########
    article_id = Column(Integer, primary_key=True, autoincrement=True, 
                                 nullable=False, index=True)

    ########## 普通列 ##########
    title = Column(String(255), nullable = False)
    content = Column(Text, nullable = False)
    picture = Column(String(255), nullable = False)
    is_draft = Column(CHAR(1), nullable = False, default = '1')
    ########## 新增 ###########
    read_num = Column(Integer,nullable=False,default=0)
    comment_num = Column(Integer,nullable=False,default=0)
    abstract = Column(Text,nullable=False)

    
    #保存文章内容图片的文件夹号，便于删除
    article_session_id = Column(String(20),nullable=False)
    ########## Index/Unique索引 ##########
    time = Column(DateTime, nullable = False, 
                            unique = False, index = True)
    favor = Column(Integer, nullable = False, 
                            unique = False, index = True, default = 0)
    category = Column(CHAR(1), nullable = False, 
                      unique = False, index = True, default = '0')
    groups = Column(CHAR(1), nullable = False, 
                      unique = False, index = True, default = '1')
    admin_read = Column(CHAR(1), nullable = False, 
                      unique = False, index = True, default = '0')
    coins = Column(Integer, nullable = False, 
                      unique = False, index = True, default = 0)

    ########## Foreign Key ##########
    user_id = Column(Integer, ForeignKey('user.user_id'), index = True,nullable = False)
    book_id = Column(Integer, ForeignKey('book.book_id'), index = True,nullable = False)
    special_id = Column(Integer, ForeignKey('special.special_id'),
                        index = True, nullable = True)

    def __init__(self, title = None, picture = None,
                       content = None, is_draft = '1',
                       time = None, category = '0',
                       groups = '1', user_id = None,
                       book_id = 1, special_id = None,article_session_id=None,abstract=None):
        self.title = title
        self.content = content
        self.picture = picture
        self.is_draft = is_draft
        self.article_session_id=article_session_id

        self.time = time
        self.favor = 0
        self.category = category
        self.groups = groups
        self.admin_read = '0'
        
        self.user_id = user_id
        self.book_id = book_id
        self.abstract = abstract
        if (special_id != None):
            self.special_id = special_id

    def __repr__(self):
        return '<Article %r>' % (self.title)
        
        
####################################  文章会话id表  ######################################

class Article_session(Base,AutoSerialize):
    __tablename__='article_session'
    __table_args__ = { 
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }
    ########## Primary索引 ##########
    article_session_id = Column(Integer, primary_key=True, 
                       autoincrement=True, nullable=False, index=True)
    
    def __init__(self):
        pass
    def __repr__(self):
        return '<Article_session: %r>' % (self.article_session_id)

class Activity_session(Base,AutoSerialize):
    __tablename__='activity_session'
    __table_args__ = { 
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }
    ########## Primary索引 ##########
    activity_session_id = Column(Integer, primary_key=True, 
                       autoincrement=True, nullable=False, index=True)
    
    def __init__(self):
        pass
    def __repr__(self):
        return '<Activity_session: %r>' % (self.activity_session_id)

##################################  评论模型  ####################################

class Comment(Base,AutoSerialize):
    __tablename__ = 'comment'
    __table_args__ = { 
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }
    __allowed_in_json__ = ['content','comment_id','time']
    ########## Primary索引 ##########
    comment_id = Column(Integer, primary_key=True, autoincrement=True, 
                                 nullable=False, index=True)

    ########## 普通列 ##########
    content = Column(Text, nullable = False)

    ########## Index/Unique索引 ##########
    time = Column(DateTime, nullable = False, 
                            unique = False, index = True)
    isgood = Column(CHAR(1), nullable = False, 
                             unique = False, index = True, default = '1')

    ########## Foreign Key ##########
    user_id = Column(Integer, ForeignKey('user.user_id'), index = True)
    to_user_id = Column(Integer, ForeignKey('user.user_id'), index = True)
    article_id = Column(Integer, ForeignKey('article.article_id'), index = True)
    reply_to_comment_id = Column(Integer, nullable=False, index=True)

       
    def __init__(self, article_id = None, content = None,
                       user_id = None, to_user_id = None,
                      reply_to_comment_id=reply_to_comment_id,time = None):
        self.content = content
        self.time = time
        self.user_id = user_id
        self.to_user_id = to_user_id
        self.article_id = article_id
        self.reply_to_comment_id = reply_to_comment_id


    def __repr__(self):
        return '<Comment id: %r>' % (self.comment_id)
        
##################################  活动评论模型  ####################################
class Comment_activity(Base,AutoSerialize):
    __tablename__ = 'comment_activity'
    __table_args__ = { 
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }

    ########## Primary索引 ##########
    comment_activity_id = Column(Integer, primary_key=True, autoincrement=True, 
                                 nullable=False, index=True)
    ########## 普通列 ##########
    content = Column(String(255), nullable = False)
    ########## Index/Unique索引 ##########
    time = Column(DateTime, nullable = False, 
                            unique = False, index = True)
    isgood = Column(CHAR(1), nullable = False, 
                             unique = False, index = True, default = '1')
    ########## Foreign Key ##########
    user_id = Column(Integer, ForeignKey('user.user_id'), index = True)
    activity_id = Column(Integer, ForeignKey('activity.activity_id'), index = True)
    
    def __init__(self, activity_id = None, content = None,
                       user_id = None, time = None):
        self.content = content
        self.time = time
        self.user_id = user_id
        self.activity_id = activity_id   
    def __repr__(self):
        return '<Comment_activity id: %r>' % (self.comment_activity_id)                
##################################  私信模型  ####################################

class Message(Base,AutoSerialize):
    __tablename__ = 'message'
    __table_args__ = { 
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }

    ########## Primary索引 ##########
    message_id = Column(Integer, primary_key=True, autoincrement=True, 
                                 nullable=False, index=True)

    ########## 普通列 ##########
    content = Column(String(255), nullable = False)

    ########## Index/Unique索引 ##########
    time = Column(DateTime, nullable = False, 
                            unique = False, index = True)

    ########## Foreign Key ##########
    user_id = Column(Integer, ForeignKey('user.user_id'), index = True)
    to_user_id = Column(Integer, ForeignKey('user.user_id'), index = True)

    def __init__(self, user_id = None, to_user_id = None,
                       content = None, time = None):
        self.content = content
        self.time = time
        self.user_id = user_id
        self.to_user_id = to_user_id


    def __repr__(self):
        return '<Message id: %r>' % (self.message_id)
        
        
##################################  活动模型  ####################################

class Activity(Base,AutoSerialize):
    __tablename__ = 'activity'
    __table_args__ = { 
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }
    __allowed_in_json__ = ['name','activity_id','activity_time']
    ########## Primary索引 ##########
    activity_id = Column(Integer, primary_key=True, autoincrement=True, 
                                  nullable=False, index=True)

    ########## 普通列 ##########
    name = Column(String(40), nullable = False)
    content = Column(Text, nullable = False)
    create_time = Column(DateTime, nullable = False)
    read_num=Column(Integer,nullable=False,default=0)
    comment_num = Column(Integer,nullable=False,default=0)
    picture=Column(String(255), nullable = False)

    #保存活动内容图片的文件夹号，便于删除
    activity_session_id = Column(String(20),nullable=False)
    abstract = Column(Text,nullable=False)
    place=Column(String(255),nullable=False)
    ########## Index/Unique索引 ##########
    favor = Column(Integer, nullable = False, 
                            unique = False, index = True, default = 0)
    state = Column(CHAR(1), nullable = False, 
                   unique = False, index = True, default = '1')
    activity_time = Column(DateTime, nullable = False, 
                           unique = False, index = True)


    def __init__(self, name = None, content = None,
                       create_time = None, activity_time = None,activity_session_id=None,picture=None,abstract=None,place=None):
        self.name = name
        self.content = content
        self.create_time = create_time
        self.activity_time = activity_time
        self.activity_session_id=activity_session_id
        self.picture=picture
        self.abstract=abstract
        self.place=place

    def __repr__(self):
        return '<Activity: %r>' % (self.name)
        
##################################  活动收藏模型  ####################################

class Collection_Activity(Base,AutoSerialize):
    __tablename__ = 'collection_activity'
    __table_args__ = { 
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }

    ########## Primary索引 ##########
    collection_activity_id = Column(Integer, primary_key=True, 
                autoincrement=True, nullable=False, index=True)

    ########## Index/Unique索引 ##########
    time = Column(DateTime, nullable = False, 
                            unique = False, index = True)

    ########## Foreign Key ##########
    user_id = Column(Integer, ForeignKey('user.user_id'), index = True)
    activity_id = Column(Integer, ForeignKey('activity.activity_id'), index = True)


    def __init__(self, user_id = None, activity_id = None,
                       time = None):
        self.user_id = user_id
        self.activity_id = activity_id
        self.time = time

    def __repr__(self):
        return '<Collection Activity id: %r>' % (self.collection_activity_id)
        

##################################  文章收藏模型  ####################################

class Collection_Article(Base,AutoSerialize):
    __tablename__ = 'collection_article'
    __table_args__ = { 
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }

    ########## Primary索引 ##########
    collection_article_id = Column(Integer, primary_key=True, 
                       autoincrement=True, nullable=False, index=True)

    ########## Index/Unique索引 ##########
    time = Column(DateTime, nullable = False, 
                            unique = False, index = True)

    ########## Foreign Key ##########
    user_id = Column(Integer, ForeignKey('user.user_id'), index = True)
    article_id = Column(Integer, ForeignKey('article.article_id'), index = True)


    def __init__(self, user_id = None, article_id = None,
                       time = None):
        self.user_id = user_id
        self.article_id = article_id
        self.time = time

    def __repr__(self):
        return '<Collection Article id: %r>' % (self.collection_article_id)
        

##################################  专栏收藏模型  ####################################

class Collection_Special(Base,AutoSerialize):
    __tablename__ = 'collection_special'
    __table_args__ = { 
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }

    ########## Primary索引 ##########
    collection_special_id = Column(Integer, primary_key=True, 
                       autoincrement=True, nullable=False, index=True)

    ########## Index/Unique索引 ##########
    time = Column(DateTime, nullable = False, 
                            unique = False, index = True)

    ########## Foreign Key ##########
    user_id = Column(Integer, ForeignKey('user.user_id'), index = True)
    special_id = Column(Integer, ForeignKey('special.special_id'), index = True)


    def __init__(self, user_id = None, special_id = None,
                       time = None):
        self.user_id = user_id
        self.special_id = special_id
        self.time = time

    def __repr__(self):
        return '<Collection Special id: %r>' % (self.collection_special_id)

##################################  用户收藏模型  ####################################

class Collection_User(Base,AutoSerialize):
    __tablename__ = 'collection_user'
    __table_args__ = { 
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }

    ########## Primary索引 ##########
    collection_user_id = Column(Integer, primary_key=True, 
                       autoincrement=True, nullable=False, index=True)

    ########## Index/Unique索引 ##########
    time = Column(DateTime, nullable = False, 
                            unique = False, index = True)

    ########## Foreign Key ##########
    user_id = Column(Integer, ForeignKey('user.user_id'), index = True)
    another_user_id = Column(Integer, ForeignKey('user.user_id'), index = True)


    def __init__(self, user_id = None, another_user_id = None,
                       time = None):
        self.user_id = user_id
        self.another_user_id = another_user_id
        self.time = time

    def __repr__(self):
        return '<Collection User id: %r>' % (self.collection_user_id)


##################################  曦潮记产品模型  ####################################

class Product(Base,AutoSerialize):
    __tablename__ = 'product'
    __table_args__ = { 
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }

    ########## Primary索引 ##########
    product_id = Column(Integer, primary_key=True, 
                       autoincrement=True, nullable=False, index=True)

    ########## 普通列 ##########
    name = Column(String(50), nullable = False)
    picture = Column(String(255), nullable = False)
    number = Column(Integer, nullable = False, default = 0)
    
    ########## Index/Unique索引 ##########
    price = Column(String(10), nullable = False, 
                            unique = False, index = True)

    def __init__(self, name = None, picture = None,
                       number = 0, price = None):
        self.name = name
        self.picture = picture
        self.number = number
        self.price = price

    def __repr__(self):
        return '<Product: %r>' % (self.name)
