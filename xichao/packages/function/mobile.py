# -*- coding: utf-8 -*-
from imports import *


def is_mobile_device(request):
    """Check if the user is from mobile device

    Args:
        request: the request from user

    Returns:
        Whether the user is using iPhone, iPad or Android
    """

    mobile_tag = request.headers.get('User-Agent')
    return (mobile_tag.find("iPhone") != -1) or \
        (mobile_tag.find("iPad") != -1) or \
        (mobile_tag.find("Android") != -1)


def is_small_mobile_device(request):
    """Check if the user is from small mobile device

    Args:
        request: the request from user

    Returns:
        Whether the user is using iPhone or Android
    """

    mobile_tag = request.headers.get('User-Agent')
    return (mobile_tag.find("iPhone") != -1) or \
        (mobile_tag.find("Android") != -1)
