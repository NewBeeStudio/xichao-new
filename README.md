# xichao-new
曦潮网站新版
====================

环境：
--------------------
 * mysql 
 * virtualenv
 * flask             //安装：`pip install Flask`
 * flask-MySQLdb     //flask-sqlalchemy的依赖包，安装：`pip install flask-sqlalchemy`
 * flask-sqlalchemy  //操作数据库，下载安装：https://pypi.python.org/pypi/MySQL-python
 * flask-wtforms     //表单渲染和验证，安装：`pip install WTForms`
 * flask.ext.mail    //安装：`pip install flask-mail`
 * flask.ext.wtf     //安装：`pip install flask_wtf`
 * flask.ext.login   //登录相关，安装：`pip install flask-login`
 * itsdangerous       //登录安全相关，安装：`pip install itsdangerous` 


框架：
--------------------
 * update.txt    //工作更新说明
 * runserver.py    //程序启动模块
 * /xichao    //python包
   + /static    //静态文件夹
   + /templates    //模板文件夹
     - test.html    //测试文件
     - test_formhelps.html    //测试文件的宏定义文件
     - test_login.html    //登陆页面测试文件
     - test_register.html    //注册页面测试文件
   + /upload    //上传文件存储
   + __init__.py    //曦潮包文件
   + ajax.py    //ajax请求处理模块
   + database.py    //数据库基本定义模块
   + models.py    //数据库表模块
   + functions.py    //通用处理函数模块
   + views.py    //视图模块
   + forms.py    //表单模块
   + myvalidators.py    //自定义验证器模块

资料：
--------------------
 * sqlalchemy：http://dormousehole.readthedocs.org/en/latest/patterns/sqlalchemy.html
               http://www.zouyesheng.com/sqlalchemy.html#toc10
 * WTForms：http://dormousehole.readthedocs.org/en/latest/patterns/wtforms.html
            http://wtforms.readthedocs.org/en/latest/fields.html
            http://docs.jinkan.org/docs/flask-wtf/index.html
 * ajax：http://dormousehole.readthedocs.org/en/latest/patterns/jquery.html
 * UEditor：http://segmentfault.com/blog/digwtx/1190000002429055
 * 进度条：http://www.developerdrive.com/2012/07/displaying-the-progress-of-tasks-with-html5/

注意事项：
--------------------
 * 安装完mysql数据库后修改编码方式，统一采用utf8，否则中文会乱码或者无法存储
 * 在mysql中创建数据库要设定编码方式为utf8


数据库建立过程：
--------------------
 * 建立名为'xichao'的数据库，命令如下：CREATE DATABASE `xichao` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;(如果数据库中已经有名为'xichao'的数据库，先将其删除)
 * 将functions.py中的导入语句'from xichao import app'注释， models.py中'from xichao import login_serializer'注释
 * terminal进入到xichao-new，再进入到xichao
 * 进入python shell（在terminal下运行'python'）
 * 运行如下语句：from database import init_db
 * 再运行导入的函数，语句为：init_db()
 * 数据库创建好后，将functions中的'from xichao import app'解除注释
 * 数据库就已经搭好了
 * 在database.py文件中将DB_URL='mysql://root:@localhost/xichao?charset=utf8'中的用户名和密码改为你们自己的，我的用户名是root，密码为空，这样就能连接到数据库了