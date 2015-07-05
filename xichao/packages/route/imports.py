# -*- coding: utf-8 -*-

from xichao import app, login_manager, login_serializer

import xichao.captcha
from xichao.functions import *
from xichao.models import User
from xichao.database import db_session
from xichao.forms import MembercardForm, \
                         RegistrationForm, \
                         LoginForm, \
                         ForgetPasswordForm, \
                         ResetPasswordForm

from flask import redirect, url_for, \
                  render_template, request, \
                  flash,session, make_response, \
                  send_from_directory, jsonify, \
                  abort,json

from flask.ext.sqlalchemy import Pagination
from flask.ext.login import LoginManager, login_user, \
                            logout_user, current_user, login_required
from wtforms import Form
from werkzeug.datastructures import ImmutableMultiDict
from itsdangerous import constant_time_compare, BadData

import json
from hashlib import md5
import os, time, urllib
from datetime import datetime,date
