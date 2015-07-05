# -*- coding: utf-8 -*-

from xichao import models
from xichao import app
from xichao.database import db_session
from xichao.models import * #User,Article,Special,Book,Comment,Article_session,Activity_session,Activity,Comment_activity,Collection_Special,Collection_User,Collection_Article,Collection_Activity,HomePage,Special_author,Special_related

from werkzeug import secure_filename
from sqlalchemy import or_, not_, and_, desc
from flask.ext.mail import Mail
from flask.ext.mail import Message
from flask.ext.sqlalchemy import Pagination
from flask import jsonify,render_template,request,session,abort

from hashlib import md5
from datetime import datetime
import re, os, shutil, urllib, json


def encrypt(password):
	encrypt_password=md5(password).hexdigest()
	return encrypt_password

def root_authorized():
	nick=None
	if 'user_id' in session:
		result = db_session.query(User).filter_by(user_id=int(session['user_id'])).all()[0]
		return result.role == 3
		## 专栏作家或者管理员
	else:
	    return False

def paginate(query,page,per_page=20,error_out=True):
	if error_out and page < 1:
		abort(404)
	items = query.limit(per_page).offset((page - 1) * per_page).all()
	if not items and page != 1 and error_out:
		abort(404)
	if page == 1 and len(items) < per_page:
		total = len(items)
	else:
		total = query.order_by(None).count()
	return Pagination(query, page, per_page, total, items)