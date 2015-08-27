# -*- coding: utf-8 -*-
from imports import *


def collection_special(user_id, special_id):
    """Create a new collection of special article by specific user

    Args:
        user_id: the id of the user
        special_id: the id of the special article
    """

    query = db_session.query(Collection_Special).filter_by(
        user_id=user_id, special_id=special_id).all()
    if len(query) == 0:
        collect_spe = Collection_Special(user_id=user_id,
                                         special_id=special_id,
                                         time=datetime.now())
        query = db_session.query(Special).filter_by(
            special_id=special_id).all()[0]
        query.favor += 1

        db_session.add(collect_spe)
        db_session.commit()

    else:
        raise Exception


def collection_special_cancel(user_id, special_id):
    """Remove the collection of special article of the specific user

    Args:
        user_id: the id of the user
        special_id: the id of the special article
    """

    query = db_session.query(Collection_Special).filter_by(
        user_id=user_id, special_id=special_id).all()
    if len(query) != 0:
        db_session.delete(query[0])
        query = db_session.query(Special).filter_by(
            special_id=special_id).all()[0]
        query.favor -= 1
        db_session.commit()

    else:
        raise Exception


def collection_special_author(user_id, author_id):
    """Create the collection relation between user and author

    Args:
        user_id: the id of the collecting user
        author_id: the id of the collected user

    Returns:
        If the user collects himslef, it returns 'self'
        If the collection already exists, it returns 'already'
        Otherwise it returns 'success'
    """

    another_user_id = author_id
    if (user_id == another_user_id):
        return "self"
    query = db_session.query(Collection_User).filter_by(
        user_id=user_id, another_user_id=another_user_id).all()
    if len(query) == 0:
        collect_usr = Collection_User(user_id=user_id,
                                      another_user_id=another_user_id,
                                      time=datetime.now())
        db_session.add(collect_usr)
        db_session.commit()
        update_collection_num(user_id, another_user_id, True)
    else:
        return "already"
    return "success"


def collection_special_author_cancel(user_id, author_id):
    """Remove the collection relation between the user and author

    Args:
        user_id: the id of the collecting user
        author_id: the id of the collected user

    Returns:
        If the user cancel the collection towards himslef, it returns 'self'
        If the collection already cancelled, it returns 'already'
        Otherwise it returns 'success'
    """

    another_user_id = author_id
    if (user_id == another_user_id):
        return "self"
    query = db_session.query(Collection_User).filter_by(
        user_id=user_id, another_user_id=another_user_id).all()
    if len(query) == 1:
        db_session.delete(query[0])
        db_session.commit()
        update_collection_num(user_id, another_user_id, False)
    else:
        return "already"
    return "success"


def create_user_collection(another_user_id, user_id):
    """Create the collection relation between user and author

    Args:
        user_id: the id of the collecting user
        author_id: the id of the collected user
    """

    result = db_session.query(Collection_User).filter(and_(
        Collection_User.user_id == user_id, Collection_User.another_user_id == another_user_id)).all()
    if len(result) > 0:
        pass
    else:
        collection = Collection_User(
            user_id=user_id, another_user_id=another_user_id, time=datetime.now())
        db_session.add(collection)
        db_session.commit()
        update_collection_num(user_id, another_user_id, True)


def delete_user_collection(another_user_id, user_id):
    """Remove the collection relation between the user and author

    Args:
        user_id: the id of the collecting user
        author_id: the id of the collected user
    """

    db_session.query(Collection_User).filter(and_(Collection_User.user_id ==
                                                  user_id, Collection_User.another_user_id == another_user_id)).delete()
    db_session.commit()
    update_collection_num(user_id, another_user_id, False)


def update_collection_num(user_id, another_user_id, is_add):
    """Update the followed number and following number of user and author

    Args:
        user_id: the id of the following user
        another_user_id: the id of the followed user
        is_add: if it is add or substract
    """

    user = db_session.query(User).filter_by(user_id=user_id).scalar()
    another_user = db_session.query(User).filter_by(
        user_id=another_user_id).scalar()
    if is_add:
        user.follow_num += 1
        another_user.be_followed_num += 1
    else:
        user.follow_num -= 1
        another_user.be_followed_num -= 1
    db_session.commit()


def collection_article(user_id, article_id):
    """Create the relation between user and article

    Args:
        user_id: the id of the user
        article_id: the id of the article

    Returns:
        If user equals the author of the article, it returns 'fail'
        If user already collected the article, it returns 'already'
        Otherwise it returns 'success'
    """

    article = db_session.query(Article).filter_by(
        article_id=article_id).first()
    result = db_session.query(Collection_Article).filter(and_(
        Collection_Article.user_id == user_id, Collection_Article.article_id == article_id)).all()
    if article.user_id == user_id:
        return 'fail'
    elif len(result) > 0:
        return 'already'
    else:
        collection_article = Collection_Article(
            user_id=user_id, article_id=article_id, time=datetime.now())
        db_session.add(collection_article)
        db_session.commit()
        return 'success'


def collection_activity(user_id, activity_id):
    """Create the relation between user and activity

    Args:
        user_id: the id of the user
        activity_id: the id of the activity

    Returns:
        If the relation already created, it returns 'already'
        Otherwise it returns 'success'
    """

    result = db_session.query(Collection_Activity).filter(and_(
        Collection_Activity.activity_id == activity_id, Collection_Activity.user_id == user_id)).all()
    if len(result) > 0:
        return 'already'
    else:
        collection_activity = Collection_Activity(
            user_id=user_id, activity_id=activity_id, time=datetime.now())
        db_session.add(collection_activity)
        db_session.commit()
        return 'success'
