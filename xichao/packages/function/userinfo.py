# -*- coding: utf-8 -*-
from imports import *


def get_user_id(nick):
    """Get userid by nickname

    Args:
        nick: the nickname of the user

    Returns:
        the user id of the nickname
    """

    user_id = db_session.query(User.user_id).filter_by(nick=nick).first()
    return user_id[0]


def getNick():
    """Get nickname

    Returns:
        The nickname of current User
    """

    nick = None
    if 'user_id' in session:
        result = db_session.query(User.nick).filter_by(
            user_id=int(session['user_id'])).first()
        nick = result[0]
    return nick


def get_avatar():
    """Get avatar

    Returns:
        THe avatar of current user
    """

    nick = getNick()
    return db_session.query(User.photo).filter_by(nick=nick).first()[0] if nick is not None else None
    # if nick is None:
    #     return None
    # avatar = db_session.query(User.photo).filter_by(nick=nick).first()
    # return avatar[0]


def get_role(user_id):
    """Get role by id

    Args:
        user_id: the id of the user

    Returns:
        The role of the user
    """

    result = db_session.query(User.role).filter_by(user_id=user_id).first()
    return result[0]


def get_user_by_nick(nick):
    """Get user by nickname

    Args:
        nick: the nickname of the user

    Returns:
        The user object
    """

    result = db_session.query(User).filter_by(nick=nick).first()
    return result


def examine_user_id(user_id):
    """Examine if user of user_id exists

    Args:
        user_id: the id of the user

    Returns:
        Whether user exists
    """

    result = db_session.query(User).filter_by(user_id=user_id).all()
    if len(result) > 0:
        return True
    else:
        return False
