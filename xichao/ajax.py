# -*- coding: utf-8 -*-
'''

		ajax请求处理模块
		
		接收前端页面发送的json格式ajax请求
		根据请求参数，形成RegistrationForm类的实例
		调用RegistrationForm类的validate()方法，形成errors信息
		根据errors信息，形成json格式的ajax响应


'''
from xichao import app
from werkzeug.datastructures import ImmutableMultiDict
from flask import request, jsonify
from forms import RegistrationForm

@app.route('/ajax_register')
def ajax_register_validate():
	email = request.args.get('email',0,type=str)
	nick = request.args.get('nick',0,type=str)
	password = request.args.get('password',0,type=str)
	confirm = request.args.get('confirm',0,type=str)
	request_form_from_ajax=ImmutableMultiDict([('email', email),('nick', nick), ('password', password), ('confirm', confirm)])
	form=RegistrationForm(request_form_from_ajax)
	form.validate()
	return jsonify(email=form.errors.get('email')[0],nick=form.errors.get('nick')[0],password=form.errors.get('password')[0],confirm=form.errors.get('confirm')[0])