# -*- coding: utf-8 -*-
from imports import *

def is_mobile_device(request):
	mobile_tag = request.headers.get('User-Agent')
	return (mobile_tag.find("iPhone") != -1) or \
		   (mobile_tag.find("iPad") != -1) or \
		   (mobile_tag.find("Android") != -1)

def is_small_mobile_device(request):
	mobile_tag = request.headers.get('User-Agent')
	return (mobile_tag.find("iPhone") != -1) or \
		   (mobile_tag.find("Android") != -1)