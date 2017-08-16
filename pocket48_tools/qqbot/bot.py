"""
这个文件是调用 https://github.com/sjdy521/Mojo-Webqq 项目的接口
在运行这个文件的方法时，需要先启动一个 Mojo-Webqq 的 server
文档见：https://github.com/sjdy521/Mojo-Webqq/blob/master/API.md
"""
import requests


class QQBot:

    def __init__(self, host='127.0.0.1', port=5000, schema='http'):
        self.schema = schema
        self.host = host
        self.port = port
        
    @property
    def url(self):
        return '{}://{}:{}'.format(schema, host, port)

    def __getattr__(self, method_name):
        """
        发送消息在这里处理
        可以调用的方法名例如：
            send_friend_message
            send_group_message
        更多可以看文件开头注释的文档
        使用方法：
            >>> bot = QQBot()
            >>> bot.send_group_message(content='hello', uid=129681496)
            >>> bot.send_friend_message(content='你好', uid=11112222)
        """
        def wrapper(**kwargs):
            url = '{}/openqq/{}'.format(self.url, method_name)
            res = requests.get(self.url, params=kwargs)
            return res
        return wrapper
