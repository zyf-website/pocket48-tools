"""
author: sljeff
email: kindjeff.com@gmail.com
"""
import datetime
import random
from queue import Queue
from threading import Thread
from time import sleep
from ..pocket import get_live_list
from .callback import dailycallback, livecallback


DELAY_DEFAULT = 20


def loop():
    today = datetime.date.today()
    delay = DELAY_DEFAULT
    while True:
        live_list = get_live_list().get('liveList')

        # 没有直播时把延时翻倍，最多到320秒
        # 有人直播时延时循环是20秒
        if live_list is None:
            delay = delay * 2 if delay < 320 else delay
        else:
            delay = DELAY_DEFAULT
            livecallback(live_list)

        # 到新的一天时触发每日任务（签到/扭蛋）
        if today < datetime.date.today():
            today = datetime.date.today()
            dailycallback()

        delay += random.randint(-3, 3)
        sleep(delay)


t_loop= Thread(target=loop, args=())
t_loop.start()
