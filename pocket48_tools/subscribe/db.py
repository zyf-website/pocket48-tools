"""
author: sljeff
email: kindjeff.com@gmail.com
"""
import datetime
import peewee
from playhouse.sqlite_ext import SqliteExtDatabase


db = SqliteExtDatabase('subscribe.db')


class BaseModel(peewee.Model):
    created_at = peewee.DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db


class Subscriptor(BaseModel):
    name = peewee.CharField(max_length=128, null=True)
    qq = peewee.IntegerField(null=True)
    email = peewee.CharField(null=True)
    pocket48_phonenum = peewee.IntegerField(unique=True, null=True)
    pocket48_password = peewee.CharField(max_length=32, null=True)
    deleted = peewee.IntegerField(default=0)


class Member(BaseModel):
    member_id = peewee.IntegerField(unique=True)
    member_name = peewee.CharField(max_length=32)
    member_room_id = peewee.IntegerField(null=True)


class LiveSubscription(BaseModel):
    subscriptor = peewee.ForeignKeyField(Subscriptor,
                                         related_name='subscriptors')
    member = peewee.ForeignKeyField(Member, related_name='subscriptors')
    deleted = peewee.IntegerField(default=0)


db.connect()
try:
    db.create_tables([Subscriptor, Member, LiveSubscription])
except peewee.OperationalError:
    pass


def get_live_subscription():
    """
    返回值格式：
        {
            成员ID: 订阅者数组,
        }
    """
    lss = LiveSubscription.select().where(LiveSubscription.deleted==0)
    result = {}
    for ls in lss:
        subscriptors = result.get(ls.member.member_id, [])
        subscriptors.append(ls.subscriptor)
        result[ls.member.member_id] = subscriptors
    return result


def get_daily_subscription():
    """
    返回值格式：
        {
            用户手机号: 用户密码,
        }
    """
    subscriptors = Subscriptor.select.where(Subscriptor.deleted==0)
    result = {}
    for s in subscriptors:
        result[s.pocket48_phonenum] = s.pocket48_password
    return result


def set_live_subscription(subscriptor, member_ids):
    """
    增加一个直播订阅。增加时会自动添加每日任务的订阅。
    subscriptor参数可以为账号密码的tuple，
    也可以只为手机号，但是这样不会进行每日任务。
    """
    if not isinstance(member_ids, (list, tuple)):
        member_ids = [member_ids]
    if isinstance(subscriptor, (list, tuple)) and len(subscriptor) == 2:
        params = {
            'pocket48_phonenum': subscriptor[0],
            'pocket48_password': subscriptor[1],
        }
    elif isinstance(subscriptor, (str, int)):
        params = {'pocket48_phonenum': subscriptor}
    else:
        return False

    try:
        s, _ = Subscriptor.get_or_create(**params)
        for mid in member_ids:
            LiveSubscription.get_or_create(
                    subscriptor=s, member=Member.get(member_id=mid))
    except peewee.OperationalError:
        return False
    return True


def set_daily_subscription(subscriptor):
    """
    仅添加每日任务的订阅。
    subscriptor参数应该为包含账号密码的tuple。
    """
    try:
        Subscriptor.get_or_create(pocket48_phonenum=subscriptor[0],
                                  pocket48_password=subscriptor[1])
    except Exception:
        return False
    return True


def del_live_subscription():
    pass


def del_daily_subscription():
    pass
