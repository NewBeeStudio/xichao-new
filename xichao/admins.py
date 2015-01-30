# -*- coding: utf-8 -*-
from xichao import app
from flask import redirect,url_for
from flask.ext.admin import Admin,BaseView,expose
from flask.ext.login import current_user,login_required,logout_user
from models import User,Article,Book,Comment,Special,Activity,Comment_activity
from database import db_session
from flask.ext.admin.contrib.sqla import ModelView

class LoginView(BaseView):
	@expose('/')
	@login_required
	def index(self):
		return self.render('admin_index.html')

class LogoutView(BaseView):
	def is_accessible(self):
		if current_user.is_authenticated():
			if current_user.role==3:
				return True
			else:
				return False
		else:
			return False
	@expose('/')
	def index(self):
		logout_user()
		return self.render('admin_logout.html')


class CreateActivityView(BaseView):
	def is_accessible(self):
		if current_user.is_authenticated():
			if current_user.role==3:
				return True
			else:
				return False
		else:
			return False
	@expose('/')
	def index(self):
		return redirect(url_for('activity_upload'))
		
		
class UserView(ModelView):
	def is_accessible(self):
		if current_user.is_authenticated():
			if current_user.role==3:
				return True
			else:
				return False
		else:
			return False
	can_create = False
	column_list=('user_id','nick','gender','email','role','state','coin','phone','member_id','birthday','slogon')
	column_searchable_list=('nick','email','phone','member_id')
	column_filters=('role','state','gender','coin')
	def __init__(self,session,**kwargs):
		super(UserView,self).__init__(User,session,**kwargs)

class ArticleView(ModelView):
	def is_accessible(self):
		if current_user.is_authenticated():
			if current_user.role==3:
				return True
			else:
				return False
		else:
			return False
	can_create = False
	column_list=('article_id','user_id','title','abstract','is_draft','read_num','comment_num','time','favor','category','groups','admin_read','coins','book_id','special_id')
	column_searchable_list=('title','abstract')
	column_filters=('is_draft','read_num','comment_num','favor','category','groups','admin_read','coins','user_id','book_id','special_id')
	def __init__(self,session,**kwargs):
		super(ArticleView,self).__init__(Article,session,**kwargs)		

class BookView(ModelView):
	def is_accessible(self):
		if current_user.is_authenticated():
			if current_user.role==3:
				return True
			else:
				return False
		else:
			return False
	can_create = False
	column_list=('book_id','title','author','press','page_num','price','press_time','binding','favor','ISBN')
	column_searchable_list=('title','author','press','binding','ISBN')
	column_filters=('author','press','ISBN')
	def __init__(self,session,**kwargs):
		super(BookView,self).__init__(Book,session,**kwargs)

class CommentView(ModelView):
	def is_accessible(self):
		if current_user.is_authenticated():
			if current_user.role==3:
				return True
			else:
				return False
		else:
			return False
	can_create = False
	column_list=('comment_id','content','time','isgood','user_id','to_user_id','article_id')
	column_filters=('isgood','user_id','to_user_id','article_id')
	def __init__(self,session,**kwargs):
		super(CommentView,self).__init__(Comment,session,**kwargs)

class SpecialView(ModelView):
	def is_accessible(self):
		if current_user.is_authenticated():
			if current_user.role==3:
				return True
			else:
				return False
		else:
			return False
	column_list=('special_id','user_id','name','introduction','article_num','time','favor','coin')
	column_filters=('user_id','article_num','favor','coin')
	def __init__(self,session,**kwargs):
		super(SpecialView,self).__init__(Special,session,**kwargs)

class ActivityView(ModelView):
	def is_accessible(self):
		if current_user.is_authenticated():
			if current_user.role==3:
				return True
			else:
				return False
		else:
			return False
	can_create = False
	column_list=('activity_id','name','content','create_time','read_num','comment_num','favor','state','activity_time')
	column_searchable_list=('name','content')
	column_filters=('read_num','comment_num','favor','state')
	def __init__(self,session,**kwargs):
		super(ActivityView,self).__init__(Activity,session,**kwargs)

class CommentActivityView(ModelView):
	def is_accessible(self):
		if current_user.is_authenticated():
			if current_user.role==3:
				return True
			else:
				return False
		else:
			return False
	can_create = False
	column_list=('comment_activity_id','content','time','isgood','user_id','activity_id')
	column_filters=('isgood','user_id','activity_id')
	def __init__(self,session,**kwargs):
		super(CommentActivityView,self).__init__(Comment_activity,session,**kwargs)		



admin=Admin(app)
admin.add_view(LoginView(name=u'登录'))
admin.add_view(LogoutView(name=u'注销'))
admin.add_view(UserView(db_session))
admin.add_view(ArticleView(db_session))
admin.add_view(BookView(db_session))
admin.add_view(CommentView(db_session))
admin.add_view(SpecialView(db_session))
admin.add_view(ActivityView(db_session))
admin.add_view(CommentActivityView(db_session))
admin.add_view(CreateActivityView(name=u'创建活动'))

