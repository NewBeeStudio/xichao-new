# -*- coding: utf-8 -*-
from imports import *


def nick_exist(nick):
    """Check if the nickname exists

    Args:
        nick: the nickname user entered

    Returns:
        Whether there are same nick name in database
    """

    result = db_session.query(User).filter_by(nick=nick).all()
    if len(result) > 0:
        return True
    else:
        return False


def is_chinese(uchar):
    """判断一个unicode是否是汉字

    Args:
        uchar: the char to check

    Returns:
        Whether the uchar in a Chinese character
    """
    if uchar >= u'\u4e00' and uchar <= u'\u9fa5':
        return True
    else:
        return False


def nick_validate(nick):
    """Check if the nickname is valid

    Args:
        nick: the nickname to be checked

    Returns:
        Whether the nickname is valid
    """

    format = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_"
    for char in nick:
        if (char not in format) and (not is_chinese(char)):
            return False
    return True


def email_exist(email):
    """Check if the email exists

    Args:
        email: the email to be checked

    Returns:
        Whether the email exists
    """

    result = db_session.query(User).filter_by(email=email).all()
    if len(result) > 0:
        return True
    else:
        return False


def cardID_exist(cardID):
    """Check if the cardID exists

    Args:
        cardID: the cardID

    Returns:
        Whether the cardID exists
    """

    result = db_session.query(User).filter_by(member_id=cardID).all()
    if len(result) > 0:
        return True
    else:
        return False

ALLOWED_EXTENSIONS = ['jpg', 'png']


def allowed_file(filename):
    """Check if the file name is valid

    Args:
        filename: the file to be checked

    Returns:
        Whether the filename is valid
    """

    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def get_state(nick, password):
    """Get the state of the user

    Args:
        nick: the nickname of the user
        password: the password of the user

    Returns:
        The state of the user or False
    """

    result = db_session.query(User).filter(
        and_(User.nick == nick, User.password == password)).all()
    if len(result) > 0:
        return result[0].state
    else:
        return False


def update_state(nick):
    """Update the state by nickname

    Args:
        nick: the nickname of the user
    """

    db_session.query(User).filter(User.nick == nick).update({'state': '1'})
    db_session.commit()


def get_secure_photoname(filename):
    """Get the secured photo name

    Args:
        filename: the filename of the photo

    Returns:
        The secured photo name
    """

    secured_filename = secure_filename(filename)
    photoname = secured_filename.rsplit('.', 1)[
        0] + datetime.now().strftime('%Y%m%d%H%M%S') + '.' + secured_filename.rsplit('.', 1)[1]
    return photoname


def send_verify_email(nick, password, email):
    """Send verify email

    Args:
        nick: the nickname of the new user
        password: the password of the new user
        email: the email of the new user

    Returns:
        Whether the email is sent successfully
    """

    verify_url = app.config['HOST_NAME'] + \
        '/verify?nick=' + nick + '&secret=' + password
    mail = Mail(app)

    msg = Message(u'曦潮书店', sender=app.config['ADMINS'][0], recipients=[email])

    msg.body = 'text body'
    msg.html = render_template(
        'test_verify_email.html', verify_url=verify_url, nick=nick)
    with app.app_context():
        try:
            mail.send(msg)
            return True
        except Exception, e:
            print "\n\n\n\n\n\n", "NoNoNoNoNoNoNo!", "\n\n\n\n\n\n"
            print str(e)
            return False
