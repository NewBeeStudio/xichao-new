# -*- coding: utf-8 -*-
from imports import *
from xichao.packages.config.user import *


def get_all_specials(sort, page_id, perpage):
    """Get paginated specials by parameters

    Args:
        sort: the sort method of all special
        page_id: the required page id
        perpage: the number of special in every page

    Returns:
        The pagination object contains the page of specific page id where every page has the given number of special sorted by the given sorting protocal
    """

    if sort == 'time':
        query = db_session.query(Special).order_by(
            Special.last_modified.desc(), Special.coin.desc())
    else:
        query = db_session.query(Special).order_by(
            Special.coin.desc(), Special.last_modified.desc())
    return paginate(query=query, page=page_id, per_page=perpage, error_out=True)


def get_search_specials(search):
    """Get searched special

    Args:
        search: the search keywords

    Returns:
        The paginated object of searched special
    """

    query = db_session.query(Special).filter(Special.name.like(
        '%' + search + '%')).order_by(Special.coin.desc())
    return paginate(query=query, page=1, error_out=True)


def create_new_special(name, picture, introduction,
                       style, total_issue, update_frequency):
    """Create new special

    Args:
        name: the special name
        picture: the picture of the article
        introduction: the introduction of the article
        style: the style of the special
        total_issue: the total_issue of the special
        update_frequency: the update frequency of the special

    Returns:
        The special id of the newly created special
    """

    time = datetime.now()
    special = Special(name=name,  # user_id = user_id,
                      picture=picture, introduction=introduction,
                      time=time, style=style,
                      total_issue=total_issue,
                      update_frequency=update_frequency)
    db_session.add(special)
#    user = db_session.query(User).filter_by(user_id = user_id).first();
#    if user.role == 1:
#        user.role = 2
    db_session.commit()
    return db_session.query(Special).filter_by(name=name).all()[0].special_id


def create_new_special_author(special_id, author):
    """Create new author of special

    Args:
        special_id: the id of the special
        author: the author of the special
    """

    special_author = Special_author(author, special_id, datetime.now())
    db_session.add(special_author)

    user = db_session.query(User).filter_by(user_id=author).first()
    # If the user was not an author, change his role
    if user.role == _ROLE_Normal_:
        user.role = _ROLE_Author_
    db_session.commit()


def has_special_author(special_id, user_id):
    """If the special and the special author is connected

    Args:
        special_id: the id of the special
        user_id: the id of the author

    Returns:
        Whether is connected
    """

    result = db_session.query(Special_author).filter(and_(
        Special_author.special_id == special_id, Special_author.user_id == user_id)).all()
    return result != []


def modify_special_func(name, authors, picture, introduction,
                        style, total_issue, update_frequency):
    """Modify special information

    Args:
        name: the name of the special
        authors: the authors of the special
        picture: the picture of the article
        introduction: the introduction of the article
        style: the style of the special
        total_issue: the total_issue of the special
        update_frequency: the update frequency of the special

    Returns:
        The id of the modified special
    """

    query = db_session.query(Special).filter_by(name=name).all()
    if (len(query) == 0):
        raise Exception
    special = query[0]
    special.picture = picture
    special.introduction = introduction
    special.style = style
    special.total_issue = total_issue
    special.update_frequency = update_frequency

    prev_authors = db_session.query(Special_author).filter(
        Special_author.special_id == special.special_id).all()
    for author in prev_authors:
        print author.user_id
        db_session.delete(author)

    for author in authors:
        special_author = Special_author(
            author, special.special_id, datetime.now())
        db_session.add(special_author)
        user = db_session.query(User).filter_by(user_id=author).first()
        if user.role == _ROLE_Normal_:
            user.role = _ROLE_Editor_

    db_session.commit()
    return special.special_id


def get_userid_by_nick(nick):
    """Get userid by nickname

    Args:
        nick: the nickname of the user

    Returns:
        the user id of the nickname
    """

    return db_session.query(User.user_id).filter_by(nick=nick).all()


def get_nick_by_userid(user_id):
    """Get nickname by user id

    Args:
        user_id: the id of the user

    Returns:
        the nickname of the user
    """

    return db_session.query(User.nick).filter_by(user_id=user_id).all()[0][0]


def get_userid_from_session():
    """Get the current user id

    Returns:
        The id of the current user
    """

    nick = None
    if 'user_id' in session:
        result = db_session.query(User).filter_by(
            user_id=int(session['user_id'])).all()
        return result[0].user_id
    return 0


def get_special_author(special_id):
    """Get authors of the special

    Args:
        special_id: the id of the special

    Returns:
        The authors
    """

    # result = db_session.query(User).filter_by(user_id = userid).all()
    result = db_session.query(User).join(Special_author).filter(
        Special_author.special_id == special_id).all()
    return result


def get_special_information(special_id):
    """Get information of the special

    Args:
        special_id: the id of the special

    Returns:
        The information
    """

    # result=db_session.query(Special,User.nick).join(User).filter(Special.special_id==special_id).all()
    result = db_session.query(Special).filter_by(special_id=special_id).all()
    if len(result) > 0:
        return result[0]
    else:
        return None


def get_special_collect_info(user_id, special_id):
    """Get how many articles in special have been collected by user

    Args:
        user_id: the id of the user
        special_id: the id of the special

    Returns:
        The number of articles collected
    """

    query = db_session.query(Collection_Special).filter_by(
        user_id=user_id, special_id=special_id).all()
    return len(query)


def get_author_collect_info(user_id, author_id):
    """Get how many articles of the author have been collected by the user

    Args:
        user_id: the id of the user
        author_id: the id of the author

    Returns:
        The number of articles collected
    """

    query = db_session.query(Collection_User).filter_by(
        user_id=user_id, another_user_id=author_id).all()
    return len(query)


def get_special_article(special_id, page_id, sort, per_page):
    """Get paginated special articles by parameters

    Args:
        sort: the sort method of all special articles
        page_id: the required page id
        perpage: the number of special articles in every page

    Returns:
        The pagination object contains the page of specific page id where every page has the given number of special articles sorted by the given sorting protocal
    """

    if sort == "time":
        query = db_session.query(Article).filter_by(
            special_id=special_id, is_draft='0').order_by(Article.time.desc())
    else:
        query = db_session.query(Article).filter_by(
            special_id=special_id, is_draft='0').order_by(Article.coins.desc())

    pagination = paginate(query=query, page=page_id,
                          per_page=per_page, error_out=True)
    return pagination


def get_special_draft(special_id):
    """Get drafts of the special

    Args:
        special_id: the id of the special

    Returns:
        The list of drafts
    """

    return db_session.query(Article).filter_by(special_id=special_id, is_draft='1').all()


def get_special_author_other(user_id, special_id, limit):
    """Get articles of the author from other place than this special

    Args:
        user_id: the id of the author
        special_id: the id of the special
        limit: the number to return

    Returns:
        The list of articles required in the given amount
    """

    query = db_session.query(Article.title, Article.article_id).filter(and_(Article.user_id == user_id, or_(
        Article.special_id is None, Article.special_id != special_id))).limit(limit).all()
    return query


def get_related_special(special_id):
    """Get related special

    Args:
        special_id: the id of the special

    Returns:
        The list of the related specials
    """

    query = db_session.query(Special).join(Special_related, Special_related.guest_id ==
                                           Special.special_id).filter(Special_related.host_id == special_id).limit(6).all()
    return query


def update_article_num_for_special(special_id, is_add):
    """Update the article number of the special

    Args:
        special_id: the id of the special
        is_add: add or substract
    """

    special = db_session.query(Special).filter_by(
        special_id=special_id).scalar()
    if is_add:
        special.article_num += 1
    else:
        special.article_num -= 1
    db_session.commit()


def prev_special_article(article_id):
    """Get previous special article

    Args:
        article_id: the id of the article

    Returns:
        The id of the previous article or None
    """

    article = db_session.query(Article).filter_by(
        article_id=article_id).first()
    if article.special_id is None:
        return None
    prev_article = db_session.query(Article).filter(and_(
        Article.special_id == article.special_id, Article.time < article.time)).order_by(Article.time.desc()).limit(1).all()
    if len(prev_article) == 0:
        return None
    else:
        return prev_article[0]


def next_special_article(article_id):
    """Get next special article

    Args:
        article_id: the id of the article

    Returns:
        The id of the next article or None
    """

    article = db_session.query(Article).filter_by(
        article_id=article_id).first()
    if article.special_id is None:
        return None
    next_article = db_session.query(Article).filter(and_(
        Article.special_id == article.special_id, Article.time > article.time)).order_by(Article.time).limit(1).all()
    if len(next_article) == 0:
        return None
    else:
        return next_article[0]
