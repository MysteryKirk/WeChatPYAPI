# 如果你是Python36。请删除37、38、39的pyd文件，其他版本同理
from WeChatPYAPI import WeChatPYApi

import time
import logging
from queue import Queue
import os
from datetime import datetime

# 当前目录路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

logging.basicConfig(level=logging.INFO)  # 日志器
msg_queue = Queue()  # 消息队列


def on_message(msg):
    """消息回调，建议异步处理，防止阻塞"""
    print(msg)
    msg_queue.put(msg)


def on_exit(event):
    """退出事件回调"""

    action = event["action"]
    wx_id = event["wx_id"]
    if action == 1:
        print("微信({})：进程结束，请重新启动微信".format(wx_id))
    elif action == 2:
        print("微信({})：已退出登录，请重新登录".format(wx_id))


def main():
    # 初次使用需要pip安装四个库：
    # pip install requests
    # pip install pycryptodomex
    # pip install psutil
    # pip install pywin32

    # 查看帮助
    help(WeChatPYApi)

    # 实例化api对象【要多开的话就实例化多个《WeChatPYApi》对象】
    w = WeChatPYApi(msg_callback=on_message, exit_callback=on_exit, logger=logging)

    # 调试模式：
    # debug_pid=日志中输出的进程pid
    # 注意：你的微信必须使用start_wx方法登录成功后，才能使用调试模式
    # w = WeChatPYApi(msg_callback=on_message, exit_callback=on_exit, logger=logging, debug_pid=15396)

    # 启动微信【调试模式可不调用该方法】
    errno, errmsg = w.start_wx()
    # errno, errmsg = w.start_wx(path=os.path.join(BASE_DIR, "login_qrcode.png"))  # 保存登录二维码
    if errno != 0:
        print(errmsg)
        if errmsg != "当前为调试模式，不需要调用“start_wx”":
            return

    # 这里需要阻塞，等待获取个人信息
    while not w.get_self_info():
        time.sleep(2)

    my_info = w.get_self_info()
    print("登陆成功！")
    print(my_info)

    # 拉取列表（好友/群/公众号等）拉取可能会阻塞，可以自行做异步处理
    # 好友列表：pull_type = 1
    # 群列表：pull_type = 2
    # 公众号列表：pull_type = 3
    # 其他：pull_type = 4
    lists = w.pull_list(pull_type=3)
    print(lists)

    # 获取朋友圈数据
    # moments = w.get_moments()
    # if not moments:
    #     print("没有最新的朋友圈")
    # else:
    #     for item in moments:
    #         print(item)

    # 获取小程序code
    # code = w.get_small_app_code(
    #     app_id="wx9e44d62c7ab75740"
    # )
    # print(code)

    # 获取群成员列表
    # lists = w.get_chat_room_members(to_chat_room="123@chatroom")
    # print(lists)

    # # 发送文本消息
    # w.send_text(to_wx="filehelper", msg='作者QQ:\r437382693')
    # time.sleep(1)

    # 发送图片消息
    # w.send_img(to_wx="filehelper", path=r"C:\Users\Administrator\Desktop\1.png")
    # time.sleep(1)

    # 发送文件/视频
    # w.send_file(to_wx="filehelper", path=r"C:\Users\Administrator\Desktop\1.mp4")
    # time.sleep(1)

    # 发送好友名片
    # w.send_friend_card(
    #     to_wx="filehelper",
    #     friend_wx=my_info["wx_id"],
    #     friend_name="三水君"
    # )
    # time.sleep(1)

    # 发送卡片链接
    # w.send_card_link(
    #     to_wx="filehelper",
    #     title="QQ",
    #     desc="437382693",
    #     target_url="http://www.baidu.com",
    #     img_url="http://img-haodanku-com.cdn.fudaiapp.com/oimg_643855036504_1627291311.jpg_310x310.jpg"
    # )
    # time.sleep(1)

    # 处理消息回调【具体根据自己的业务来写，这里只是一个简陋的演示】
    while True:
        msg = msg_queue.get()

        # 正常消息
        if msg["type"] == 100:
            # 自己发送的消息
            if msg["is_self_msg"]:
                print("收到了自己发送的消息！")

            # 别人发送的消息
            else:
                if msg["msg_type"] == 37:
                    # 同意添加好友申请
                    w.agree_friend(msg_data=msg)

                # 处理图片消息
                elif msg["msg_type"] == 3:
                    file_path, file_name = os.path.split(msg["file_path"])
                    if file_name.endswith("dat"):
                        cur_time = datetime.now().strftime("%Y-%m-%d %H-%M-%S ")
                        file_name = cur_time + file_name.replace(".dat", "")
                        print(file_name)

                        # 这里睡2秒是防止某些图片过大，还未完全下载完毕
                        time.sleep(2)

                        # 保存图片
                        w.save_img(
                            save_path=os.path.join(BASE_DIR, "temp\\{}.png".format(file_name)),
                            msg_data=msg,
                        )

                # 收款
                elif msg["msg_type"] == 490:
                    is_recv = msg["detail"]["is_recv"]
                    if is_recv:
                        # 收款
                        w.collection(msg_data=msg)

        # 撤回消息
        # 注意：撤回消息中的参数，跟正常消息的参数不一致，可自行判断type是否是666，分别放到不同的队列中处理
        elif msg["type"] == 666:
            print("{} 撤回消息：{}".format(msg["wx_id"], msg["content"]))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        os._exit(1)
