# -*- coding: utf-8 -*-
from xichao import app
from flask.ext.admin import Admin,BaseView,expose

class MyView(BaseView):
	@expose('/')
	def index(self):
		return self.render('admin_index.html')

admin=Admin(app)
admin.add_view(MyView(name=u'测试'))