#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import threading
from flask import Flask
import signal
from argparse import ArgumentParser
import sqlite3
import mc.getUrlTest as McTest
import mc.groupSign as groupSign
from configuration import Config
from constants import ChatType
from db.mysqlDb import MySQLConnectionPool
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


def init_group_info(robot: Robot) -> None:
    receivers = robot.config.NEWS

    for r in receivers:
        group_info = robot.getRoomInfo(r)
        # 初始化群聊 {'wxid_1538135380812': '莫城', 'wxid_ej6qv9p6r6bg22': '乌苏里江畔', 'wxid_ytllv9po50bj12': 'CikL.'}
        for wxid, name in group_info.items():
            groupSign.init_group_info(r, wxid, name)

    robot.LOG.info(f"初始化群聊成功")

def reminderSignInfo(robot: Robot) -> None:
    receivers = robot.config.NEWS

    for r in receivers:
        info = groupSign.reminderSignInfo(r)
        robot.sendTextMsg(McTest.get_weather_api(), r)



    robot.LOG.info(f"初始化群聊成功")


@app.route('/test')
def send_message_to_robot():
    robot.LOG.info(f"执行测试...")
    robot.sendTextMsg("Hello from Flask!", "filehelper")
    return "OK"

def main(chat_type: int):

    global robot, wcf  # 确保这些变量是全局的，以便在线程中访问
    config = Config()
    wcf = Wcf(debug=True)

    # 初始化
    mysql_util = MySQLConnectionPool(host=config.MySql.get('host'), user=config.MySql.get('user'), password=config.MySql.get('password'), database=config.MySql.get('database'))
    def handler(sig, frame):
        wcf.cleanup()  # 退出前清理环境
        exit(0)

    signal.signal(signal.SIGINT, handler)

    robot = Robot(config, wcf, chat_type)

    robot.LOG.info(f"WeChatRobot【{__version__}】成功启动···")
    # 初始化群聊
    init_group_info(robot)

    # 机器人启动发送测试消息
    robot.sendTextMsg("机器人启动成功！", "filehelper")


    # 接收消息
    # robot.enableRecvMsg()     # 可能会丢消息？
    robot.enableReceivingMsg()  # 加队列
    # 每天 8 点发送天气预报
    robot.onEveryTime("08:00", weather_report, robot=robot)
    # 每天 7 点初始化群聊
    robot.onEveryTime("07:00", init_group_info, robot=robot)

    # 每天 8:30 发送新闻
     # robot.onEveryTime("08:30", robot.newsReport)

    # 每天 18:00 提醒发日报周报月报
    #  robot.onEveryTime("18:00", ReportReminder.remind, robot=robot)

    # 每天 23:00 提醒 签到详情
    # robot.onEveryTime("23:00", reminderSignInfo, robot=robot)

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

    parser = ArgumentParser()
    parser.add_argument('-c', type=int, default=0, help=f'选择模型参数序号: {ChatType.help_hint()}')
    args = parser.parse_args().c
    main(args)

