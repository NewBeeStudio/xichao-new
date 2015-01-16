# xichao-new
曦潮网站新版

环境：
  mysql
  virtualenv
  flask
  flask-MySQLdb    //flask-sqlalchemy的依赖包
  flask-sqlalchemy    //操作数据库
  flask-wtforms    //表单渲染和验证

框架：
  update.txt    //工作更新说明
  runserver.py    //程序启动模块
  /xichao    //python包
    /static    //静态文件夹
    /templates    //模板文件夹
    /upload    //上传文件存储
    __init__.py    //曦潮包文件
    ajax.py    //ajax请求处理模块
    database.py    //数据库基本定义模块
    models.py    //数据库表模块
    functions.py    //处理函数模块
    views.py    //视图模块
    forms.py    //表单模块
    myvalidators.py    //自定义验证器模块

注意事项：
  安装完mysql数据库后修改编码方式，统一采用utf8，否则中文会乱码或者无法存储
  在mysql中创建数据库要设定编码方式为utf8
