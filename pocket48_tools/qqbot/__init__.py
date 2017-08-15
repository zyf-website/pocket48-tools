from .bot import QQBot


qqbot = QQBot()

def qqpush(subcriptors, live_data):
    qqbot.send_group_message(content=live_data['title'], uid=129681496)
