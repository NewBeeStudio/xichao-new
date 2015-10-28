# -*- coding: utf-8 -*-
from imports import *
from xichao.packages.config.article import *
from xichao.packages.config.user import *

# 分页函数
# 源自官方的实现


def paginate(query, page, per_page=20, error_out=True):
    """Paginate the query by paremeters

    Args:
        query: the query to be paginated
        page: the page number
        per_page: the item number per page
        error_out:

    Returns:
        The Pagination object with paremeters
    """
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


def create_message(to_user_id, user_id, content):
    """Create message between user

    Args:
        to_user_id: the id of to-user
        user_id: the id of the user
        content: the content of the message
    """

    message = models.Message(
        user_id=user_id, to_user_id=to_user_id, content=content, time=datetime.now())
    # message=models.Message(user_id,to_user_id,content,datetime.now())
    db_session.add(message)
    db_session.commit()


def create_notification(user_id, content):
    """Create the notification of the user

    Args:
        user_id: the id of the user
        content: the content of the notification
    """

    user_list = db_session.query(User).filter(User.role != 3).all()
    for user in user_list:
        create_message(user.user_id, user_id, content)


def user_coin_add(user_id, num):
    """Add user coin

    Args:
        user_id: the id of the user
        num: the amount to be added
    """

    user = db_session.query(User).filter_by(user_id=user_id).scalar()
    user.coin += num
    db_session.commit()


def user_coin_sub(user_id, num):
    """Substract user coin

    Args:
        user_id: the id of the user
        num: the amount to be substract
    """

    user = db_session.query(User).filter_by(user_id=user_id).scalar()
    user.coin -= num
    db_session.commit()


def special_coin_add(special_id, num):
    """Add special coin

    Args:
        special_id: the id of the special
        num: the amount to be added
    """

    special = db_session.query(Special).filter_by(
        special_id=special_id).scalar()
    special.coin += num
    db_session.commit()


def article_coin_add(article_id, num):
    """Add article coin

    Args:
        article_id: the id of the article
        num: the amount to be added
    """

    article = db_session.query(Article).filter_by(
        article_id=article_id).scalar()
    article.coins += num
    if (article.groups == _GROUP_Special_):
        special_coin_add(article.special_id, num)
    db_session.commit()
    article = db_session.query(Article).filter_by(
        article_id=article_id).first()
    user_coin_add(user_id=article.user_id, num=num)


def process_article_award(user_id, article_id, award_num):
    """Award the article from user

    Args:
        user_id: the id of the awarding user
        article_id: the id of the awarded article
        award_num: the amount to be awarded

    Returns:
        If the user is the author himself, it returns 'fail'
        Otherwise it returns 'success'
    """

    article = db_session.query(Article).filter_by(
        article_id=article_id).first()
    if article.user_id == user_id:
        return 'fail'
    else:
        user_coin_sub(user_id=user_id, num=award_num)
        article_coin_add(article_id=article_id, num=award_num)
        add_pay_record(user_id=user_id, article_id=article_id,
                       award_num=award_num)
        return 'success'


def add_pay_record(user_id, article_id, award_num):
    """Add the payment record

    Args:
        user_id: the id of the user
        article_id: the id of the article
        award_num: the amount to be awarded
    """

    record = models.Pay_Record(
        user_id=user_id, article_id=article_id, coins=award_num, time=datetime.now())
    db_session.add(record)
    db_session.commit()


def examine_article_id(article_id):
    """Check if the article exists

    Args:
        article_id: the id of the article

    Returns:
        If the article exists
    """

    result = db_session.query(Article).filter_by(article_id=article_id).all()
    if len(result) > 0:
        return True
    else:
        return False


def update_article_favor(article_id, is_add):
    """Add or substract the favor of article

    Args:
        article_id: the id of the article
        is_add: if the number is added
    """

    article = db_session.query(Article).filter_by(
        article_id=article_id).scalar()
    if is_add:
        article.favor += 1
    else:
        article.favor -= 1
    db_session.commit()


def update_activity_favor(activity_id, is_add):
    """Add or substract the favor of activity

    Args:
        article_id: the id of the activity
        is_add: if the number is added
    """

    activity = db_session.query(Activity).filter_by(
        activity_id=activity_id).scalar()
    if is_add:
        activity.favor += 1
    else:
        activity.favor -= 1
    db_session.commit()


def get_current_activity_list(time):
    """Get the list of current activities

    Args:
        time: currenet time

    Returns:
        the list of current activities
    """

    result = db_session.query(Activity).filter(
        Activity.activity_time > time).all()
    return result


def get_passed_activity_list(time):
    """Get the list of passed activities

    Args:
        time: current

    Returns:
        the list of passed activities
    """

    result = db_session.query(Activity).filter(Activity.activity_time < time).order_by(
        desc(Activity.activity_time)).limit(4).all()
    return result


def get_follow_num(user_id):
    """Get the following number

    Args:
        user_id: the id of the user

    Returns:
        The following number
    """

    result = db_session.query(Collection_User).filter_by(user_id=user_id).all()
    return len(result)


def get_be_followed_num(user_id):
    """Get the followed number

    Args:
        user_id: the id of the user

    Returns:
        The followed number
    """

    result = db_session.query(Collection_User).filter_by(
        another_user_id=user_id).all()
    return len(result)


def get_article_pagination_by_user_id(user_id, by_time, page_id):
    """Get the article pagination object by paremeters

    Args:
        user_id: the id of the user
        by_time: if the pagination is sorted by time
        page_id: the page number

    Returns:
        The pagination object by paremeters
    """

    if by_time:
        query = db_session.query(Article).filter(and_(
            Article.user_id == user_id, Article.is_draft == '0', Article.special_id is None)).order_by(desc(Article.time))
    else:
        query = db_session.query(Article).filter(and_(
            Article.user_id == user_id, Article.is_draft == '0', Article.special_id is None)).order_by(desc(Article.coins))
    return paginate(query, page_id, 5, False)


def get_collection_author_list(user_id):
    """Get the list of all collection authors

    Args:
        user_id: the id of the user

    Returns:
        The list of authors
    """
    result = db_session.query(User).join(Collection_User, Collection_User.another_user_id ==
                                         User.user_id).filter(Collection_User.user_id == user_id).all()
    return result


def get_comment_pagination_by_user_id(user_id, page_id):
    """Get the pagination object by user

    Args:
        user_id: the id of the user
        page_id: the page number

    Returns:
        The pagination object of comments
    """

    query = db_session.query(Comment, Article).join(Article).filter(
        Comment.user_id == user_id).order_by(desc(Comment.time))
    return paginate(query, page_id, 4, False)


def get_article_draft_pagination(user_id, page_id):
    """Get the pagination object of drafts

    Args:
        user_id: the id of the user
        page_id: the page number

    Returns:
        The pagination object of drafts
    """

    query = db_session.query(Article).filter(
        and_(Article.user_id == user_id, Article.is_draft == '1'))
    return paginate(query, page_id, 5, False)


def get_article_collection_pagination(user_id, page_id):
    """Get the pagination object of article collections

    Args:
        user_id: the id of the user
        page_id: the page number

    Returns:
        The pagination object of article collections
    """

    query = db_session.query(Article, Collection_Article, User).join(Collection_Article, Collection_Article.article_id ==
                                                                     Article.article_id).join(User, User.user_id == Article.user_id).filter(Collection_Article.user_id == user_id)
    return paginate(query, page_id, 5, False)


def get_activity_collection_pagination(user_id, page_id):
    """Get the pagination object of activity collections

    Args:
        user_id: the id of the user
        page_id: the page number

    Returns:
        The pagination object of activity collections
    """

    query = db_session.query(Activity, Collection_Activity).join(
        Collection_Activity, Collection_Activity.activity_id == Activity.activity_id).filter(Collection_Activity.user_id == user_id)
    return paginate(query, page_id, 5, False)


def get_user_collection_pagination(user_id, page_id):
    """Get the pagination object of user collections

    Args:
        user_id: the id of the user
        page_id: the page number

    Returns:
        The pagination object of user collections
    """

    query = db_session.query(User, Collection_User).join(
        Collection_User, Collection_User.another_user_id == User.user_id).filter(Collection_User.user_id == user_id)
    return paginate(query, page_id, 10, False)


def get_special_collection_pagination(user_id, page_id):
    """Get the pagination object of special collection

    Args:
        user_id: the id of the user
        page_id: the page number

    Returns:
        The pagination object of special collection
    """

    query = db_session.query(Special, Collection_Special).join(
        Collection_Special, Collection_Special.special_id == Special.special_id).filter(Collection_Special.user_id == user_id)
    return paginate(query, page_id, 10, False)


def get_fans_pagination(user_id, page_id):
    """Get the pagination object of fans

    Args:
        user_id: the id of the user
        page_id: the page number

    Returns:
        The pagination object of fans
    """

    query = db_session.query(User).join(Collection_User, Collection_User.user_id == User.user_id).filter(
        Collection_User.another_user_id == user_id)
    return paginate(query, page_id, 10, False)


def get_message_pagination(user_id, page_id):
    """Get the pagination object of message

    Args:
        user_id: the id of the user
        page_id: the page number

    Returns:
        The pagination object of message
    """

    query = db_session.query(models.Message, User).join(User, User.user_id == models.Message.user_id).filter(
        and_(models.Message.to_user_id == user_id, User.role != _ROLE_Root_)).order_by(desc(models.Message.time))
    return paginate(query, page_id, 4, False)


def get_received_comment_pagination(user_id, page_id):
    """Get the pagination object of received comment

    Args:
        user_id: the id of the user
        page_id: the page number

    Returns:
        The pagination object of received comment
    """

    query = db_session.query(Comment, User, Article).join(User, User.user_id == Comment.user_id).join(
        Article, Article.article_id == Comment.article_id).filter(Comment.to_user_id == user_id).order_by(desc(Comment.time))
    return paginate(query, page_id, 4, False)


def get_notification_pagination(user_id, page_id):
    """Get the pagination object of notification

    Args:
        user_id: the id of the user
        page_id: the page number

    Returns:
        The pagination object of notification
    """

    query = db_session.query(models.Message).join(User, User.user_id == models.Message.user_id).filter(
        and_(models.Message.to_user_id == user_id, User.role == _ROLE_Root_)).order_by(desc(models.Message.time))
    return paginate(query, page_id, 4, False)


def get_special_pagination(user_id, page_id):
    """Get the pagination object of special

    Args:
        user_id: the id of the user
        page_id: the page number

    Returns:
        The pagination object of special
    """

    query = db_session.query(Special).join(
        Special_author).filter(Special_author.user_id == user_id)
    return paginate(query, page_id, 3, False)


def get_has_prev(pagination):
    """Get if it has previous page

    Args:
        pagination: the pagination object

    Returns:
        If the previous page exists, it returns 'yes'
        Otherwise it returns 'no'
    """

    if pagination.has_prev:
        return 'yes'
    else:
        return 'no'


def get_has_next(pagination):
    """Get if it has next page

    Args:
        pagination: the pagination object

    Returns:
        If the next page exists, it returns 'yes'
        Otherwise it returns 'no'
    """

    if pagination.has_next:
        return 'yes'
    else:
        return 'no'


def updata_user_basic_information_by_user_id(user_id, nick, gender, birthday, phone):
    """Update the basic information

    Args:
        user_id: the id of the user
        nick: the nick name of the user
        gender: the gender of the user
        birthday: the birthday of the user
        phone: the phone of the user

    Returns:
        If there's no birthday, it returns 'success_no_birthday'
        If there's no phone, it returns 'success_no_phone'
        If there's no birthday or phone, it returns 'success_no_birthday_phone'
        Otherwise it returns 'success'
    """

    user = db_session.query(User).filter_by(user_id=user_id).scalar()
    user.nick = nick
    user.gender = gender
    user.birthday = birthday
    user.phone = phone
    db_session.commit()
    if birthday is None and phone is not None:
        return 'success_no_birthday'
    elif birthday is not None and phone is None:
        return 'success_no_phone'
    elif birthday is None and phone is None:
        return 'success_no_birthday_phone'
    else:
        return 'success'


def delete(file_path):
    """Delete file by path

    Args:
        file_path: the path of deleting file

    Returns:
        If delete successfully, it returns 'delete file success'
        Otherwise it returns 'delete file fail'
    """

    file_path_list = file_path.split('/')
    file_path_list_length = len(file_path_list)
    filename = file_path_list[file_path_list_length - 1]
    if filename in app.config['DEFAULT_FILE']:
        pass
    else:
        try:
            os.remove(os.path.join(os.path.dirname(__file__), file_path[1:]))
            print 'delete file success'
        except Exception, e:
            print 'delete file fail'
            print e


def update_user_avatar(user_id, avatar):
    """Update user avatar

    Args:
        user_id: the id of the user
        avatar: the image of avatar

    Returns:
        'success'
    """

    user = db_session.query(User).filter_by(user_id=user_id).scalar()
    old_avatar = user.photo
    user.photo = avatar
    db_session.commit()
    delete(old_avatar)
    return 'success'


def update_user_cover(user_id, cover):
    """Update user cover

    Args:
        user_id: the id of the user
        cover: the cover image

    Returns:
        'success'
    """

    user = db_session.query(User).filter_by(user_id=user_id).scalar()
    old_cover = user.cover
    user.cover = cover
    db_session.commit()
    delete(old_cover)
    return 'success'


def update_user_slogon(user_id, slogon):
    """Update user slogon

    Args:
        user_id: the id of the user
        slogon: the user slogon

    Returns:
        'success'
    """

    user = db_session.query(User).filter_by(user_id=user_id).scalar()
    user.slogon = slogon
    db_session.commit()
    return 'success'


def update_member_id(user_id, member_id):
    """Update member id

    Args:
        user_id: the id of the user
        member_id: the id of the member

    Returns:
        'success' unless update failed
    """

    user = db_session.query(User).filter_by(user_id=user_id).scalar()
    user.member_id = member_id
    try:
        db_session.commit()
        return 'success'
    except:
        return 'fail'


# 获取发表的文章数目 start


def get_article_number(user_id):
    """Get the number of the articles

    Args:
        user_id: the id of the user

    Returns:
        The number of the article
    """

    result = db_session.query(Article).filter(and_(
        Article.user_id == user_id, Article.is_draft == '0', Article.groups != _GROUP_Special_)).all()
    return len(result)


# 获取发表的文章数目 end
# 获取消息数目 start


def get_message_number(user_id):
    """Get the number of message

    Args:
        user_id: the id of the user

    Returns:
        The number of the message
    """

    result = db_session.query(models.Message).join(User, User.user_id == models.Message.user_id).filter(
        and_(models.Message.to_user_id == user_id, models.Message.is_read == '0', User.role != _ROLE_Root_)).all()
    return len(result)


def get_comment_number(user_id):
    """Get the number of comment

    Args:
        user_id: the id of the user

    Returns:
        The number of the comment
    """

    result = db_session.query(Comment).filter(
        and_(Comment.to_user_id == user_id, Comment.is_read == '0')).all()
    return len(result)


def get_notification_number(user_id):
    """Get the number of notifications

    Args:
        user_id: the id of the user

    Returns:
        The number of the notifications
    """

    result = db_session.query(models.Message).join(User, User.user_id == models.Message.user_id).filter(
        and_(models.Message.to_user_id == user_id, models.Message.is_read == '0', User.role == _ROLE_Root_)).all()
    return len(result)


# 获取消息数目 end
# 更新消息阅读状态 start


def update_message_read_state_by_message_id(message_id):
    db_session.query(models.Message).filter(
        models.Message.message_id == message_id).update({'is_read': '1'})
    db_session.commit()


def update_comment_read_state_by_comment_id(comment_id):
    """Update the read state of comment

    Args:
        comment_id: the id of the comment
    """

    db_session.query(Comment).filter(Comment.comment_id ==
                                     comment_id).update({'is_read': '1'})
    db_session.commit()


def update_notification_read_state_by_notification_id(notification_id):
    """Update the notification read state

    Args:
        notification_id: the id of the notification
    """

    update_message_read_state_by_message_id(notification_id)


def update_message_read_state(message_pagination):
    """Update the message read state

    Args:
        message_pagination: the pagination object of messages
    """

    for item in message_pagination.items:
        update_message_read_state_by_message_id(item[0].message_id)


def update_comment_read_state(comment_pagination):
    """Update the comment read state

    Args:
        comment_pagination: the pagination object of comments
    """

    for item in comment_pagination.items:
        update_comment_read_state_by_comment_id(item[0].comment_id)


def update_notification_read_state(notification_pagination):
    """Update the notification read state

    Args:
        notification_pagination: the pagination object of notifications
    """

    for item in notification_pagination.items:
        update_notification_read_state_by_notification_id(item.message_id)


# 更新消息阅读状态 end


def get_recommend_words():
    """Get rocomend words

    Returns:
        The recommend word
    """
    result = db_session.query(HomePage.recommend_words).first()
    return result


def get_point_by_member_id(member_id):
    """Get point of a member

    Args:
        member_id: the id of the member

    Returns:
        The actual point
    """

    try:
        member_data = urllib.urlopen(
            'http://shjdxcsd.xicp.net:4057/website_read.aspx?Secret=18A6E54B00574FD5C172C52C3D689C8E&CardID=' + member_id).read()
        member_data = member_data.split('}')[0] + '}'
        memberDB = json.loads(member_data)
    except:
        return 0
    try:
        point = int(memberDB["coin"])
    except:
        return 0
    return point


def get_suggest_user():
    """Get 曦潮叶子

    Returns:
        The user:曦潮叶子
    """

    return db_session.query(User).filter_by(nick=u"曦潮叶子").first()
