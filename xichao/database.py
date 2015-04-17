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

DB_URL='mysql://root:Xichao42@localhost/xichao?charset=utf8'
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

    ## 对初始化进行测试
    test_db()


def test_db():
    # test_size > 10
    test_size = 15
    Total_Article = 0
    Total_Activity = 0
    ##先导入操作数据库所需的所有函数
    from functions import encrypt
    from time import sleep
    ##上传路径
    ##关于上传路径是前端的事情,这里的url只是示例,具体url格式由前端决定
    
    
    ##添加主页信息
    from models import HomePage
    home = HomePage(special1 = 1, special2 = 3, special3 = 5, special4 = 7)
    db_session.add(home)
    db_session.commit()
    
    ##测试用户
    from datetime import datetime, timedelta
    from models import User

    for i in range(test_size):
        user = User(nick = "Nick%d"%(i+1), email = "example%d@example.com"%(i+1), 
                    role = 1, register_time = datetime.now(),
                    slogon = u"用户 Nick%d 的个人介绍！" % (i+1),
                    last_login_time = datetime.now(), password = encrypt(u"password"),
                    state = '1',photo=u"/upload/avatar/default.jpg")
        db_session.add(user)
        db_session.commit()

    ##测试管理员
    user = User(nick = u"曦潮", email = u"xichao@xichao.com", 
                role = 3, register_time = datetime.now(),
                slogon = u"我是管理员！",
                last_login_time = datetime.now(), password = encrypt(u"xichao"),
                state = u'1',photo=u'upload/avatar/default1.jpg')
    db_session.add(user)
    db_session.commit()
    
    ##测试书籍
    from models import Book
    book = Book(title = u"GRE核心词汇考法精析", ISBN = u"9787802562547",
                       picture =u"http://img3.douban.com/lpic/s7642485.jpg", author = u"陈琦,周书林",
                       press = u"群言出版社", page_num = u"449",
                       price = u"55.00元", press_time=u"2011-9",binding="平装")
    db_session.add(book)
    db_session.commit()

    ##测试专栏
    from models import Special
    for i in range(test_size):
        special = Special(name = u"Nick%d的专栏"%(i+1), user_id = i+1,
                           picture = u"/upload/special/special_upload_pic.jpg", 
                           introduction = u"Nick%d的专栏 的简介"%(i+1),
                           time = datetime.now())
        db_session.add(special)
        db_session.commit()
        sleep(1)


    ##添加专栏文章，每个专栏10篇
    from models import Article
    for special_id in range(1, test_size+1):
        for i in range(10):
            Total_Article += 1
            article = Article(title = u"Nick%d的专栏 的 第%d篇文章"%(special_id, i+1), 
                              picture = u"/upload/article/article_title_image/article_upload_pic_1.jpg",
                              content = u"本文是 Nick%d的专栏 的 第%d篇文章 的内容"%(special_id, i), is_draft = '0',
                              time = datetime.now(), 
                              category = '1',    ## 1表示书评，2表示影评，3表示杂文
                              groups = '3',     ## 1表示广场，2表示文章，3表示专栏
                              user_id = special_id, ##special_id和user_id在test创建中是一样的
                              book_id = 1, special_id = special_id,
                              article_session_id = Total_Article, abstract = u"Nick%d的专栏 的 第%d篇文章 的摘要"%(special_id, i))
            db_session.add(article)
            db_session.commit()
            
    ##添加10篇广场书评
    for i in range(10):
        Total_Article += 1
        article = Article(title = u"第%d篇 广场书评"%(i+1), 
                          picture = u"/upload/article/article_title_image/article_upload_pic_1.jpg",
                          content = u"本文是 第%d篇 广场书评 的内容"%(i+1), is_draft = '0',
                          time = datetime.now(), 
                          category = '1',    ## 1表示书评，2表示影评，3表示杂文
                          groups = '1',     ## 1表示广场，2表示文章，3表示专栏
                          user_id = i + 1, ##special_id和user_id在test创建中是一样的
                          book_id = 1, 
                          article_session_id = Total_Article, abstract = u"第%d篇 广场书评 的摘要"%(i+1))
        db_session.add(article)
        db_session.commit()

    ##添加10篇广场影评
    for i in range(10):
        Total_Article += 1
        article = Article(title = u"第%d篇 广场影评"%(i+1), 
                          picture = u"/upload/article/article_title_image/article_upload_pic_1.jpg",
                          content = u"本文是 第%d篇 广场影评 的内容"%(i+1), is_draft = '0',
                          time = datetime.now(), 
                          category = '2',    ## 1表示书评，2表示影评，3表示杂文
                          groups = '1',     ## 1表示广场，2表示文章，3表示专栏
                          user_id = i + 1, ##special_id和user_id在test创建中是一样的
                          book_id = 1, 
                          article_session_id = Total_Article, abstract = u"第%d篇 广场影评 的摘要"%(i+1))
        db_session.add(article)
        db_session.commit()

    ##添加10篇广场杂文
    for i in range(10):
        Total_Article += 1
        article = Article(title = u"第%d篇 广场杂文"%(i+1), 
                          picture = u"/upload/article/article_title_image/article_upload_pic_1.jpg",
                          content = u"本文是 第%d篇 广场杂文 的内容"%(i+1), is_draft = '0',
                          time = datetime.now(), 
                          category = '3',    ## 1表示书评，2表示影评，3表示杂文
                          groups = '1',     ## 1表示广场，2表示文章，3表示专栏
                          user_id = i + 1, ##special_id和user_id在test创建中是一样的
                          book_id = 1, 
                          article_session_id = Total_Article, abstract = u"第%d篇 广场杂文 的摘要"%(i+1))
        db_session.add(article)
        db_session.commit()


    ##添加对应的Article_session
    from models import Article_session
    for i in range(Total_Article):
      article_session = Article_session()
      db_session.add(article_session)
      db_session.commit()

    
    ##测试评论
    """
    from models import Comment
    comment = Comment(article_id = 1, content = u"这篇文章写的真好啊！",
                       user_id = 2, to_user_id = 1,
                       time = datetime.now())
    db_session.add(comment)
    db_session.commit()
    """
    
    

    ##测试私信
    """
    from models import Message
    message = Message(user_id = 1, to_user_id = 2,
                      content = u"谢谢你评论我的文章", time = datetime.now())
    db_session.add(message)
    db_session.commit()
    """



    ##添加过去活动
    from models import Activity
    for i in range(5):
        ##曦潮童汇
        Total_Activity += 1
        activity = Activity(name = u"曦潮童汇 第%d期"%(i+1), content = u"小朋友们看过来",
                            create_time = datetime.now(), 
                            activity_time = datetime.now(),
                            activity_session_id=Total_Activity,
                            picture=u'/upload/activity/activity_title_image/activity_upload_pic_1.jpg',
                            abstract=u"小朋友们看过来......",place=u"曦潮书店") 
        db_session.add(activity)
        db_session.commit()

    ##添加未来活动
    from models import Activity
    for i in range(5):
        ##曦潮童汇
        Total_Activity += 1
        activity = Activity(name = u"曦潮童汇 第%d期"%(i+6), content = u"小朋友们看过来",
                            create_time = datetime.now(), 
                            activity_time = datetime.now() + timedelta(days=100),
                            activity_session_id=Total_Activity,
                            picture=u'/upload/activity/activity_title_image/activity_upload_pic_1.jpg',
                            abstract=u"小朋友们看过来......",place=u"曦潮书店") 
        db_session.add(activity)
        db_session.commit()


    ##测试活动会话id
    from models import Activity_session
    for i in range(Total_Activity):
        activity_session=Activity_session()
        db_session.add(activity_session)
        db_session.commit()
    

    ##测试对活动的评论
"""
    from models import Comment_activity
    comment_activity = Comment_activity(activity_id=1,content=u"这个活动真赞啊",user_id=1,time=datetime.now())
    db_session.add(comment_activity)
    db_session.commit()
"""

"""    
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
"""
