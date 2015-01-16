
from xichao import app
from hashlib import md5
from models import User
from database import db_session
from flask import jsonify

'''

def user_exist(username):
	return result




def get_user_encrypt_password(username):
	return password


def create_user(username,password):
	return True
'''

def nick_exist(nick):
	result=db_session.query(User).filter_by(nick=nick).all()
	if len(result)>0:
		return True
	else:
		return False

@app.route('/_email_exist')
def email_exist():
	email=request.args.get('email',0,type=string)
	result=db_session.query(User).filter_by(email=email).all()
	if len(result)>0:
		return jsonify(code=403)
	else:
		return jsonify(code=200)

def user_exist(username):
	result=db_session.query(User).filter_by(nick=username).all()
	if len(result)>0:
		return True
	else:
		return False

def encrypt(password):
	encrypt_password=md5(password).hexdigest()
	return encrypt_password