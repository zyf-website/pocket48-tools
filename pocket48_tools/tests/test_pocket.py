from ..pocket import get_live_list, PocketSession


# 测试 pocket 获取直播链接
live_list = get_live_list()
if 'reviewList' not in live_list:
    print('获取直播链接失败')
    exit()


# 测试 pocket Session
with PocketSession(13211112222, 'jeffjeff') as s:
    if not s.is_login:
        print('登录失败')
        exit()
    sign_result = s.sign()
    print(sign_result)

    live_list = s.get_live_list()
    print(live_list['reviewList'][0])

    today_member = s.get_today_member()
    print(today_member)

    room_list = s.get_room_list()
    print(room_list[1])
    room_id = room_list[1]['roomId']
    print(room_id)

    niudans = s.get_niudan()
    if niudans is not None:
        niudan = niudans[0]
        print(niudan)


print('pocket测试完成')
