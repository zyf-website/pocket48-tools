"""
author: sljeff
email: kindjeff.com@gmail.com
"""
from . import db
from .callback import update_subscription
from ..pocket import PocketSession


def subscribe_member_live(subscriptor, member_ids):
    db.set_live_subscription(subscriptor, member_ids)
    update_subscription()


def subscribe_daily_task(subscriptor):
    db.set_daily_subscription(subscriptor)
    update_subscription()


def unsubscribe_member_live(subscriptor, member_ids=None):
    db.del_live_subscription(subscriptor, member_ids)
    update_subscription()


def unsubscribe_daily_task(subscriptor):
    db.del_daily_subscription(subscriptor)
    update_subscription()
