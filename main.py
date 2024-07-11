#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import threading
from flask import Flask
import signal
from argparse import ArgumentParser
import sqlite3
import mc.getUrlTest as McTest
from threading import Thread, Event

from base.func_report_reminder import ReportReminder
from configuration import Config
from constants import ChatType

from robot import Robot, __version__
from wcferry import Wcf

app = Flask(__name__)
def weather_report(robot: Robot) -> None:
    """模拟发送天气预报
    """

    # 获取接收人 文件传输助手
    # receivers = ["filehelper"]
    #
    receivers = robot.config.REPORT_REMINDERS
    if not receivers:
        receivers = ["filehelper"]
    for r in receivers:
        robot.sendTextMsg(McTest.get_weather_api(), r)

        # robot.sendTextMsg(report, r, "notify@all")   # 发送消息并@所有人


def send_image2(robot: Robot) -> None:
    robot.sendImage(McTest.test_send_image(""), "filehelper")
@app.route('/test')
def send_message_to_robot():
    robot.LOG.info(f"执行测试...")
    robot.sendTextMsg("Hello from Flask!", "filehelper")
    return "OK"

def main(chat_type: int):
    chat_type =3
    global robot, wcf  # 确保这些变量是全局的，以便在线程中访问
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


def start_flask_app():
    app.run(host='0.0.0.0', port=8888, debug=True, use_reloader=False)

if __name__ == "__main__":
    # 创建并启动 Flask 应用的线程
    flask_thread = threading.Thread(target=start_flask_app)
    flask_thread.daemon = True  # 设置为守护线程
    # 启动线程
    flask_thread.start()
    # 创建并启动 main 函数的线程
    main(3)

