"""
author: sljeff
email: kindjeff.com@gmail.com
"""
from . import db
from ..pocket import PocketSession
from ..qqbot import qqpush


live_subscription = {}
daily_subscription = {}
daily_sessions = {}
live_members = {}


def update_subscription():
    """
    从数据库里更新订阅信息。应该在每次数据库更改时调用。
    """
    global live_subscription, daily_subscription, daily_sessions
    live_subscription = db.get_live_subscription()
    daily_subscription = db.get_daily_subscription()

    for phonenum in daily_sessions.keys():
        if phonenum not in daily_subscription.keys():
            daily_sessions.pop(phonenum)

    for phonenum, password in daily_subscription.items():
        if daily_sessions.get(phonenum) is None:
            daily_sessions[phonenum] = PocketSession(phonenum, password)


update_subscription()


def livecallback(live_list):
    """
    直播的回调函数。
    每次会和上一次比较，检查新的直播成员是否被订阅，并进行推送。
    """
    global live_members
    _live_members = {l['memberId']: l for l in live_list}
    new_member_ids = set(_live_member_ids.keys()) - set(live_member_ids.keys())
    live_members = _live_members

    for mid in new_member_ids:
        subscriptors = live_subscription.get(mid)
        if subscriptors is not None:
            live_data = live_members.get(mid)
            qqpush(subscriptors, live_data)


def dailycallback():
    """
    日常任务的回调（签到/扭蛋）。
    只会在签到失败时进行一次重新登录。
    """
    for session in daily_sessions.values():
        sign_result = session.sign()
        if sign_result is None:
            session.login()
            sign_result = session.sign()
        session.get_niudan()
