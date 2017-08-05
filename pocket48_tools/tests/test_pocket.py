from ..pocket import get_live_list, PocketSession


# 测试 pocket 获取直播链接
live_list = get_live_list()
if 'reviewList' not in live_list:
    print('获取直播链接失败')


print('pocket测试完成')
