from xichao import app
from werkzeug.datastructures import ImmutableMultiDict
from flask import request, jsonify
from forms import RegistrationForm

@app.route('/ajax_register')
def ajax_register_validate():
	email = request.args.get('email',0,type=unicode)
	nick = request.args.get('nick',0,type=unicode)
	password = request.args.get('password',0,type=unicode)
	confirm = request.args.get('confirm',0,type=unicode)
	request_form_from_ajax=ImmutableMultiDict([('email', email),('nick', nick), ('password', password), ('confirm', confirm)])
	form=RegistrationForm(request_form_from_ajax)
	form.validate()
	return jsonify(email=form.errors.get('email')[0],nick=form.errors.get('nick')[0],password=form.errors.get('password')[0],confirm=form.errors.get('confirm')[0])