# -*- coding: utf-8 -*-
from imports import *


def create_activity(title, content, title_image, activity_session_id, activity_time, abstract, place):
    """Create new activity by session id

    If the activity of the activity session id exists, modify it into the new activity according to the parameters and retrieve the activity id. Otherwise create a new activity and retrieve the new activity id.

    Args:
        title: the title of the new activity
        content: the content of the new activity
        title_image: the image of the new activity
        activity_session_id: the session id of the new activity
        activity_time: the time of the new activity
        abstract: the abstract of the new activity
        place: the place of the new activity

    Returns:
        The activity id of the newly created activity.
    """
    result = db_session.query(Activity).filter_by(
        activity_session_id=activity_session_id).all()
    if len(result) > 0:
        activity = db_session.query(Activity).filter_by(
            activity_session_id=activity_session_id).scalar()
        activity.name = title
        activity.content = content
        activity.picture = title_image
        activity.create_time = datetime.now()
        activity.activity_time = activity_time
        activity.abstract = abstract
        activity.place = place
        db_session.commit()
        return activity.activity_id
    else:
        activity = Activity(name=title, content=content, picture=title_image, create_time=datetime.now(
        ), activity_session_id=activity_session_id, activity_time=activity_time, abstract=abstract, place=place)
        db_session.add(activity)
        db_session.commit()
        result = db_session.query(Activity).filter_by(
            activity_session_id=activity_session_id).first()
        return result.activity_id


def get_passed_activity_pagination(sort, page_id, perpage):
    """Get paginated activities by parameters

    Args:
        sort: the sort method of all activities
        page_id: the required page id
        perpage: the number of activities in every page

    Returns:
        The pagination object contains the page of specific page id where every page has the given number of activities sorted by the given sorting protocal
    """

    if sort == 'time':
        query = db_session.query(Activity).order_by(
            Activity.activity_time.desc(), Activity.favor.desc())
    else:
        query = db_session.query(Activity).order_by(
            Activity.favor.desc(), Activity.activity_time.desc())
    return paginate(query=query, page=page_id, per_page=perpage, error_out=True)


def get_activity_information(activity_id):
    """Get the specific activity

    Args:
        activity_id: the id of the activity

    Returns:
        The information of the activity with the given id

    """
    result = db_session.query(Activity).filter_by(
        activity_id=activity_id).all()
    if len(result) > 0:
        return result[0]
    else:
        return None


def get_activity_comments(activity_id):
    """Get the list of comments of the artical in specific id

    Args:
        activity_id: the id of target activity

    Returns:
        The comment list of the requested activity
    """

    result = db_session.query(Comment_activity, User.nick, User.photo).join(User, Comment_activity.user_id == User.user_id).filter(
        Comment_activity.activity_id == activity_id).order_by(desc(Comment_activity.time)).all()
    if len(result) > 0:
        return result
    else:
        return None


def update_read_num_activity(activity_id):
    """Add the read number record of the speciifc activity

    Args:
        activity_id: the id of target activity
    """

    activity = db_session.query(Activity).filter_by(
        activity_id=activity_id).scalar()
    activity.read_num += 1
    db_session.commit()


def create_activity_comment(content, activity_id):
    """Create new comment to the specific activity

    Args:
        content: the comment content
        activity_id: the id of target activity
    """

    user_id = int(session['user_id'])
    comment_activity = Comment_activity(
        activity_id=activity_id, content=content, user_id=user_id, time=datetime.now())
    db_session.add(comment_activity)
    db_session.commit()


def update_activity_comment_num(activity_id):
    """Add comment number of the specific activity

    Args:
        activity_id: the id of target activity
    """

    activity = db_session.query(Activity).filter_by(
        activity_id=activity_id).scalar()
    activity.comment_num += 1
    db_session.commit()
