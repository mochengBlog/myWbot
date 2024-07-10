#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import threading
import signal

from configuration import Config

from robot import Robot, __version__
from wcferry import Wcf
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/info')
def submit():
    # 在这里执行表单数据处理的逻辑
    return 'Form submitted successfully!'

def main(chat_type: int):
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.start()
    config = Config()
    wcf = Wcf(debug=True)

    def handler(sig, frame):
        wcf.cleanup()  # 退出前清理环境
        exit(0)

    signal.signal(signal.SIGINT, handler)

    robot = Robot(config, wcf, chat_type)
    robot.LOG.info(f"WeChatRobot【{__version__}】成功启动···")

    # 机器人启动发送测试消息
    robot.sendTextMsg("机器人启动成功！", "filehelper")

    # 接收消息
    # robot.enableRecvMsg()     # 可能会丢消息？
    robot.enableReceivingMsg()  # 加队列


    # 让机器人一直跑
    robot.keepRunningAndBlockProcess()
    flask_thread.join()



def run_flask_app():
    app.run()
if __name__ == "__main__":
    main(3)
