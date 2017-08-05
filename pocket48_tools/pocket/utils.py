"""
author: sljeff
email: kindjeff.com@gmail.com
"""
import requests


def get_imei_str():
    # TODO
    return '867875026844420'


class PocketSession(requests.Session):
    """
    继承自 requests.Session
    用此类的实例进行所有网络操作失败时，会自动重试三次
    用法：
        >>> from ..pocket import PocketSession
        >>> session = PocketSession(13511112222, 'jeffjeff')
        >>> sign_result = session.sign()  # 签到
        >>> session.close()
        >>> # 或者
        >>> with PocketSession(13511112222, 'jeffjeff') as s:
        >>>     member_id = s.get_today_member()
        >>>     s.sign()
    """

    def __init__(self, phonenum=None, password=None):
        """
        创建实例时传手机号和密码时会登录，实例可以执行所有方法
        未登录时可以执行 login 和 get_live_list 方法
        """
        super().__init__()
        self.__prepare_header()
        self.mount('https://', requests.adapters.HTTPAdapter(max_retries=3))
        self.mount('http://', requests.adapters.HTTPAdapter(max_retries=3))

        self.is_login = False
        self.phonenum = phonenum
        self.password = password
        self.login()
    
    def login(self, phonenum=None, password=None):
        """
        登录

        如果在已经登录的状态下调用其他方法总是出错，
        可以试试不带参数调用这个方法来进行重新登录。
        也可以使用这个方法并且带上手机号和密码参数来登录一个账号。
        （如果你需要同时操作两个账号，你应该另外创建一个 Session）
        """
        if phonenum is not None:
            self.phonenum = phonenum
        if password is not None:
            self.password = password
        if self.phonenum is None or self.password is None:
            return

        url = 'https://puser.48.cn/usersystem/api/user/v1/login/phone'
        data = {
            'latitude': '0',
            'longitude': '0',
            'password': str(self.password),
            'userid': str(self.phonenum),
        }
        res = self.post(url, json=data).json()
        if res['status'] == 200:
            self.login_data = res['content']
            self.headers['token'] = self.login_data['token']
            self.juju_headers['token'] = self.login_data['token']
            self.is_login = True
            return True
        return False

    def sign(self):
        """
        签到
        """
        if not self.is_login:
            return

        url = 'https://puser.48.cn/usersystem/api/user/v1/check/in'
        res = self.post(url, json={})
        return self.content_or_none(res)

    def get_niudan(self):
        """
        扭蛋

        返回值格式为：
            [{
                "emoticon": {
                    "filePath": 动图URL（host为https://source.48.cn）,
                    "filePath2": "",
                    "filePath2Small": "",
                    "filePathSmall": "",
                    "id": 图片ID,
                    "picPath": 静态图URL（host为https://source.48.cn）,
                    "star": 星级（1 2 3）,
                    "team": "TEAM NII",
                    "title": "董艳芸的加油",
                    "type": "SNH48 TEAM NII",
                    "typeChinese": "SNH48 TEAM NII"
                },
                "freeTimes": 0,
                "restMoney": 17,
                "template": "",
                "todayIsFree": false,
                "type": 0
            },]
        """
        if not self.is_login:
            return

        url = 'https://pother.48.cn/othersystem/api/toymachine/v1/play'
        data = {
            "auth": self.login_data['token'],
            "from": 0,
            "playCount": 1,
            "toyMachineId": 1,
            "userId": self.login_data['userInfo']['userId'],
            "version": "v2",
        }
        res = self.post(url, json=data, headers=self.niudan_headers)
        content = self.content_or_none(res)
        if content is not None:
            return content['awards']
        return None

    def get_live_list(self):
        """
        获取直播列表

        返回值格式为：
            {
                "giftUpdTime": 1498211389003,
                "giftUpdUrl": [],
                "hasReviewUids":[回看的ID列表],
                "reviewList": [
                    {
                        "liveId": 直播ID,
                        "liveType": 1,
                        "lrcPath": 弹幕URL（host为https://source.48.cn）,
                        "memberId": 327587,
                        "picLoopTime": 0,
                        "picPath": 封面URL（host为https://source.48.cn）,
                        "screenMode": 0,
                        "startTime": 1501908376162,
                        "streamPath": 直播链接,
                        "subTitle": "hi",
                        "title": "冯思佳的直播间"
                    },
                ],
                "liveList": [{格式同reviewList}, ]
            }
        """
        url = 'https://plive.48.cn/livesystem/api/live/v1/memberLivePage'
        data = {
            "giftUpdTime": 1498211389003,
            "groupId": 0,
            "lastTime": 0,
            "limit": 60,
            "memberId": 0,
            "type": 0,
        }
        if self.is_login:
            data['visitorId'] = self.login_data['userInfo']['userId']

        res = self.post(url, json=data, headers=self.live_headers)
        return self.content_or_none(res)

    def get_today_member(self):
        """
        获取今日有缘成员

        返回值是成员ID
        """
        if not self.is_login:
            return

        url = 'https://puser.48.cn/usersystem/api/user/member/v1/random/get/one'
        res = self.post(url, json={}).json()
        content = self.content_or_none(res)
        if content is not None:
            return content['memberId']
        return None

    def get_room_list(self, page=1):
        """
        获取聚聚房间列表

        返回值格式为：
            [{
                "bgPath": "#EAD4EB",
                "disabledJoin": false,
                "disabledMessage": false,
                "fontColor": "",
                "groupId": 0,
                "hot": 130334,
                "lastCommentInfo": "[文字消息]",
                "lastCommentTime": "2017-08-05 14:38:00",
                "memberId": 63,
                "memberName": "袋王",
                "mood": "1",
                "moodName": "元气满满",
                "moodPicBig": "/mediasource/mood/yuanqimanman_big.png",
                "moodPicSmall": "/mediasource/mood/yuanqimanman_small.png",
                "moodPicTop": "/mediasource/mood/yuanqimanman_top.png",
                "role": 0,
                "roomAvatar": "/mediasource/room/1500276701118YUJfCN8RC5.jpg",
                "roomId": 5774517,
                "roomName": "深圳卫视极速前进",
                "roomType": 2,
                "topGiftUserId": 3271,
                "topic": "今晚22:00 绵羊和大哥（今晚婷婷代班）等你！",
                "voteMemberId": 0
            },]
        """
        if not self.is_login:
            return

        url = 'https://pjuju.48.cn/imsystem/api/im/v1/member/room/hot'
        data = {
            "groupId": 0,
            "needRootRoom": true,
            "page": page,
            "topMemberIds": []
        }
        res = self.post(url, json=data, headers=self.juju_headers)
        content = self.content_or_none(res)
        if content is not None:
            return content['data']
        return None

    def get_room_msg(self, room_id):
        """
        获取房间的成员消息

        返回值格式为：
            [{
                "bodys": "emm..monster还得多练练(＞_＜)",
                "extInfo": ,
                "msgTime": 1501917495161,
                "msgTimeStr": "2017-08-05 15:18:15",
                "msgType": 0,
                "msgidClient": "42dfb4ef-22c1-4ba5-a353-2f58f488eea2",
                "userId": 0
            },]
            其中的 extInfo 是翻牌信息的json字符串（翻牌时上面的bodys为空）
            extInfo 解包后的格式：
                {'build': 18000,
                'chatBackgroundBubbles': 0,
                'content': '',
                'contentType': 1,
                'dianzanNumber': 0,
                'faipaiContent': '准备上高铁了 下午就能看到小狮子了好开心',
                'faipaiName': '暖冬\u3000',
                'faipaiPortrait': '/mediasource/avatar/342109.png',
                'faipaiUserId': 342109,
                'fromApp': 2,
                'messageObject': 'faipaiText',
                'messageText': '记得买份午饭 公演见～',
                'platform': 'ios',
                'referenceNumber': 0,
                'role': 2,
                'roomType': 1,
                'senderAvatar': '/mediasource/avatar/1498582316911FwD69eM3N8.jpg',
                'senderHonor': '',
                'senderId': 480656,
                'senderLevel': 'HIII',
                'senderName': '董思佳',
                'senderRole': 1,
                'source': 'juju',
                'sourceId': '7900792',
                'version': '2.1.2'}
        """
        if not self.is_login:
            return

        url = 'https://pjuju.48.cn/imsystem/api/im/v1/member/room/message/chat'
        data = {
            "lastTime": 0,
            "limit": 10,
            "roomId": int(room_id),
        }
        res = self.post(url, json=data, headers=self.juju_headers)
        content = self.content_or_none(res)
        if content is not None:
            return content['data']
        return None

    def get_room_comment(self, room_id):
        """
        获取房间的用户评论

        返回值格式为：
            {
                "data": [
                    {
                        "bodys": "下午能看见了",
                        "extInfo":,
                        "msgTime": 1501912051012,
                        "msgTimeStr": "2017-08-05 13:47:31",
                        "msgType": 0,
                        "msgidClient": "3c7869cf-408a-4e0f-9c09-51ec8210db94",
                        "userId": 0
                    },
                ],
                "lastTime": 1501893856838,
                "top1Data": {
                    "bodys": "",
                    "extInfo": ,
                    "msgTime": 1501665073811,
                    "msgTimeStr": "2017-08-02 17:11:13",
                    "msgType": 0,
                    "msgidClient": "3a2764480dd14498a417c837da71f32a",
                    "userId": 0
                }
            }
            其中的extInfo为用户信息的json字符串，解包后的格式为：
                {'build': 32282,
                'content': '',
                'contentType': 1,
                'fromApp': 2,
                'messageObject': 'messageBoard',
                'platform': 'ios',
                'role': -1,
                'roomType': 1,
                'senderAvatar': '/mediasource/avatar/1498811240989A6RhJeZ5TI.jpg',
                'senderHonor': '/mediasource/badge/small/xuanbajuju@2x.png',
                'senderId': 109211,
                'senderLevel': 'LV5',
                'senderName': '上进青年陈某',
                'senderRole': 0,
                'source': 'juju',
                'sourceId': '7900792',
                'text': '下午能看见了',
                'version': '4.1.6'}
        """
        if not self.is_login:
            return

        url = 'https://pjuju.48.cn/imsystem/api/im/v1/member/room/message/'\
              'comment'
        data = {
            "lastTime": 0,
            "limit": 10,
            "roomId": int(room_id),
        }
        res = self.post(url, json=data, headers=self.juju_headers)
        return self.content_or_none(res)

    def __prepare_header(self):
        """
        注：下面header里面的一些字段设置成通用且相同值的也可以运行，
        但是为了防止特征太过明显被发现，给每个动作都设置抓包到的header
        """
        self.imei = get_imei_str()
        self.headers = {
            'Accept':'text/html,application/xhtml+xml,application/xml;'\
                     'q=0.9,*/*;q=0.8',
            'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'IMEI': self.imei,
            'User-Agent': 'Mobile_Pocket',
            'token': '0',
            'os': 'android',
            'version': '4.0.4',
            'Content-Type': 'application/json;charset=utf-8',
            'Host': 'puser.48.cn',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip',
        }
        self.live_headers = {
            'IMEI': self.imei,
            'User-Agent': 'Mobile_Pocket',
            'token': '0',
            'os': 'android',
            'version': '4.0.4',
            'Content-Type': 'application/json;charset=utf-8',
            'Host': 'plive.48.cn',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip',
        }
        self.niudan_headers = {
            'Host': 'pother.48.cn',
            'Content-Type': 'application/json;utf-8',
            'Origin': 'https://h5.48.cn',
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_2 like Mac '\
                          'OS X) AppleWebKit/603.2.4 (KHTML, like Gecko) Mobil'\
                          'e/14F89',
            'Referer': 'https://h5.48.cn/game/niudan2017/?from=1&needlogin=1',
            'Accept-Language': 'zh-cn',
            'Accept-Encoding': 'gzip, deflate',
        }
        self.juju_headers = {
            'Host': 'pjuju.48.cn',
            'app-type': 'fans',
            'Accept': '*/*',
            'version': '4.1.6',
            'os': 'ios',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-Hans-CN;q=1',
            'imei': self.imei,
            'token': '',
            'User-Agent': 'Mobile_Pocket',
            'Content-Length': '60',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json;charset=utf-8',
        }

    def content_or_none(self, res):
        if isinstance(res, requests.models.Response):
            if res.status_code != 200:
                return None
            res = res.json()
        if not isinstance(res, dict):
            return None

        if res['status'] == 200:
            return res['content']
        return None


def get_live_list():
    return PocketSession().get_live_list()
