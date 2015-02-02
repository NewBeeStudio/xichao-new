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
engine = create_engine(DB_URL, echo=True, convert_unicode=True)

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


#建立数据库时一定要建立成utf8编码的，mysql的相应字符配置需要更改
def init_db():
    import models
    Base.metadata.create_all(bind=engine)

    # 对初始化进行测试
    test_db()


def test_db():
    ##先导入操作数据库所需的所有函数
    from functions import encrypt
    ##上传路径
    ##关于上传路径是前端的事情,这里的url只是示例,具体url格式由前端决定
        
    ##测试用户
    from datetime import datetime
    from models import User
    user = User(nick = "Nick1", email = "example1@exmample.com", 
                role = 1, register_time = datetime.now(),
                slogon = u"我要吃遍大江南北！",
                last_login_time = datetime.now(), password = encrypt(u"password"),
                state = '0',photo=u'http://127.0.0.1:5000/upload/avatar/default.jpg')
    db_session.add(user)
    db_session.commit()

    
    user = User(nick = u"Nick2", email = u"example2@exmample.com", 
                role = 1, register_time = datetime.now(),
                slogon = u"我要吃遍大江南北！",
                last_login_time = datetime.now(), password = encrypt(u"password"),
                state = u'0',photo=u'http://127.0.0.1:5000/upload/avatar/default1.jpg')
    db_session.add(user)
    db_session.commit()

    user = User(nick = u"曦潮", email = u"xichao@xichao.com", 
                role = 3, register_time = datetime.now(),
                slogon = u"我是管理员！",
                last_login_time = datetime.now(), password = encrypt(u"xichao"),
                state = u'1',photo=u'http://127.0.0.1:5000/upload/avatar/default1.jpg')
    db_session.add(user)
    db_session.commit()    
    ##测试书籍
    from models import Book
    book = Book(title = u"算法导论", ISBN = u"7111407016",
                       picture =u"http://127.0.0.1:5000/book/picture/test.jpg", author = u"Thomas H.Cormen",
                       press = u"机械工业出版社", page_num = u"780",
                       price = u"￥91.10", press_time=u"2012年12月",binding="平装")
    db_session.add(book)
    db_session.commit()

    ##测试专栏
    from models import Special
    special = Special(name = u"这里都是好吃的", user_id = 1,
                       picture = u"http://127.0.0.1:5000/upload/special/special_detail_pic_1.png", 
                       introduction = u"带你吃遍上海美食^_^",
                       time = datetime.now())
    db_session.add(special)
    db_session.commit()

    from models import Special
    special = Special(name = u"算法学习指南", user_id = 2,
                       picture = u"http://127.0.0.1:5000/upload/special/special_detail_pic_2.jpg", 
                       introduction = u"""
                       <div>
                       本专栏专门用来引导算法初学者，让大家更多的体会到算法之美
                       </div>
                       <table>
 				<tr>
    				<td>作者</td>
    				<td> Nick2 </td>
  				</tr>
  				<tr>
    				<td>类别</td>
    				<td>饮食/专栏</td>
  				</tr>
  				<tr>
    				<td>期数</td>
    				<td>共11期，正在更新</td>
  				</tr>
				</table>""",
                       time = datetime.now())
    db_session.add(special)
    db_session.commit()

    ##测试文章会话id

    from models import Article_session
    for i in range(20):
      article_session = Article_session()
      db_session.add(article_session)
      db_session.commit()
    
    ##测试文章
    from models import Article
    from time import sleep
    for i in range(10):
        article = Article(title = u"算法入门%d"%(i), picture = u"http://127.0.0.1:5000/upload/article/article_title_image/article_upload_pic_1.jpg",
                          content = u"本文是算法入门文章%d"%(i), is_draft = '1',
                          time = datetime.now(), category = '1',    ## 0表示 TODO 1表示 TODO 2 表示 TODO
                          groups = '1', user_id = 1,             ## 1表示 TODO
                          book_id = 1, special_id = 2,article_session_id = i+1, abstract = u"本文是算法入门文章")
        db_session.add(article)
        db_session.commit()
        sleep(1)

    for i in range(10):
        article = Article(title = u"吃货之家%d"%(9-i), picture = u"http://127.0.0.1:5000/upload/article/article_title_image/article_upload_pic_1.jpg",
                          content = u"本文是吃货入门文章%d"%(i), is_draft = '1',
                          time = datetime.now(), category = '1',    ## 0表示 TODO 1表示 TODO 2 表示 TODO
                          groups = '1', user_id = 1,             ## 1表示 TODO
                          book_id = 1, special_id = 1,article_session_id = i+11, abstract = u"本文是吃货入门文章")
        db_session.add(article)
        db_session.commit()
        sleep(1)




    ##测试活动会话id

    from models import Activity_session
    activity_session=Activity_session()
    db_session.add(activity_session)
    db_session.commit()

    
    ##测试评论
    from models import Comment
    comment = Comment(article_id = 1, content = u"这篇文章写的真好啊！",
                       user_id = 2, to_user_id = 1,
                       time = datetime.now())
    db_session.add(comment)
    db_session.commit()
    
    

    ##测试私信
    from models import Message
    message = Message(user_id = 1, to_user_id = 2,
                      content = u"谢谢你评论我的文章", time = datetime.now())
    db_session.add(message)
    db_session.commit()
    
    ##测试活动
    from models import Activity
    activity = Activity(name = u"曦潮童汇", content = u"小朋友们看过来",
                        create_time = datetime.now(), 
                        activity_time = datetime.now(),activity_session_id=1,picture='http://127.0.0.1:5000/upload/activity/activity_title_image/activity_upload_pic_1.jpg',abstract=u"小朋友们看过来......",place=u"曦潮书店") 
                        ##注意这里活动时间不应该是now
    db_session.add(activity)
    db_session.commit()

    ##测试对活动的评论
    from models import Comment_activity
    comment_activity = Comment_activity(activity_id=1,content=u"这个活动真赞啊",user_id=1,time=datetime.now())
    db_session.add(comment_activity)
    db_session.commit()
    
    ##测试活动收藏
    from models import Collection_Activity
    collect_act = Collection_Activity(user_id = 1, 
                                      activity_id = 1,
                                      time = datetime.now())
    db_session.add(collect_act)
    db_session.commit()
    
    ##测试文章收藏
    from models import Collection_Article
    collect_art = Collection_Article(user_id = 2, 
                                     article_id = 1,
                                     time = datetime.now())
    db_session.add(collect_art)
    db_session.commit()
    
    ##测试专栏收藏
    from models import Collection_Special
    collect_spe = Collection_Special(user_id = 2, 
                                     special_id = 1,
                                     time = datetime.now())
    db_session.add(collect_spe)
    db_session.commit()
    
    ##测试用户收藏
    from models import Collection_User
    collect_usr = Collection_User(user_id = 2, 
                                  another_user_id = 1,
                                  time = datetime.now())
                                  #用户2收藏用户1
    db_session.add(collect_usr)
    db_session.commit()
    
    ##测试曦潮记产品
    from models import Product
    product = Product(name = u"明信片", picture = u"URL for 产品图片",
                      number = 100, price = u"￥5.00")
    db_session.add(product)
    db_session.commit()
