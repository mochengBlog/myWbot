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


def main(chat_type: int):
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

    send_image2(robot)
    # 每天 7 点发送天气预报
    robot.onEveryTime("08:00", weather_report, robot=robot)

    # 每天 8:30 发送新闻
    robot.onEveryTime("08:30", robot.newsReport)

    # 每天 18:00 提醒发日报周报月报
    robot.onEveryTime("18:00", ReportReminder.remind, robot=robot)

    # 让机器人一直跑
    robot.keepRunningAndBlockProcess()



def apptest():
    app.run(host='0.0.0.0', port=8888, debug=True)

if __name__ == "__main__":
    #parser = ArgumentParser()
    #parser.add_argument('-c', type=int, default=0, help=f'选择模型参数序号: {ChatType.help_hint()}')
    #args = parser.parse_args().c

    Thread(target=apptest, args=[0]).start()
    main(3)
