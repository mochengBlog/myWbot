#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import threading
from flask import Flask, request
import signal
from argparse import ArgumentParser
import sqlite3
import mc.getUrlTest as McTest
import mc.groupSign as groupSign
from configuration import Config
from constants import ChatType
from db.pySql import DBConnectionPool, DBUtils
from mc.duo_lin_guo import check_duolingo_status
from mc.func_doImage import get_task_process, save_image_by_url
from robot import Robot, __version__
from wcferry import Wcf
import pymysql

from configuration import Config

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


def get_mj_info(robot: Robot) -> None:
    rows = robot.dbUtils.execute_query("select * from mj_info where mj_url is null")
    if not rows:
        pass
        # print("No rows found.")
    else:
        for row in rows:
            task_id = row['task_id']
            #去查询接口看是否生成
            response = get_task_process(task_id)
            data = response.json()
            robot.LOG.info(data)
            # 处理数据
            if data['status'] == 'IN_PROGRESS':
                pass
                # robot.sendTextMsg("任务进度：" + str(data['progress']), row['room_id'], row['sender_id'])
            elif data['status'] == 'FAILURE':
                robot.sendTextMsg("任务失败", row['room_id'], row['sender_id'])
            elif data['status'] == 'SUCCESS':
                robot.dbUtils.update('mj_info', {'mj_url': data['imageUrl']}, 'task_id = ' + str(task_id))
                robot.sendTextMsg("任务成功，图像地址：" + data['imageUrl'], row['room_id'], row['sender_id'])
                robot.sendImage(save_image_by_url(data['imageUrl']), row['room_id'])
            else:
                robot.sendTextMsg("爷欠费了：" + str(data['status']), row['room_id'], row['sender_id'])



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


@app.route('/sentToWxId', methods=['GET'])
def sentToWxId():
    wxid = request.args.get('wxid')  # 从 URL 查询参数中获取 wxid
    msg = request.args.get('msg')  # 从 URL 查询参数中获取 text
    robot.LOG.info(f"发送消息到 {wxid} : {msg}")
    robot.sendTextMsg(str(msg), str(wxid))  # 发送消息
    return "发送消息成功", 200


def init_group_info_mysql(robot: Robot, db_utils: DBUtils) -> None:
    db_utils.execute_query("truncate table room_info")
    receivers = db_utils.execute_query("select room_id from messages group by room_id ");
    for r in receivers:
        # 获取字典r的值
        r = r['room_id']
        group_info = robot.getRoomInfo(r)
        # 初始化群聊 {'wxid_1538135380812': '莫城', 'wxid_ej6qv9p6r6bg22': '乌苏里江畔', 'wxid_ytllv9po50bj12': 'CikL.'}
        for wxid, name in group_info.items():
            #查询该room_id 下的wxid是否存，若存在 判断name是否相等
            db_utils.insert("room_info", {"room_id": r, "vxid": wxid, "name": name})

def check_duolingo(robot: Robot, db_utils: DBUtils) -> None:
    user_map = db_utils.getDuoLinGuoUser()
    status_dict = check_duolingo_status(user_map)
    robot.sendTextMsg("多邻国打卡结果", "43541810338@chatroom")
    # 将所有用户的打卡状态合并到一个字符串中
    status_lines = []
    for name, status in status_dict.items():
        if status.get("status") == "error":
            status_lines.append(f"{name}: {status['message']}")
        else:
            status_lines.append(f"{name} {status['status']}")

    db_utils.DuoLinGuoSignInsert(status_dict,"43541810338@chatroom")
    # 使用换行符连接所有状态信息并打印
    robot.sendTextMsg('\n'.join(status_lines), "43541810338@chatroom")


def main(chat_type: int):
    global robot, wcf, db_utils  # 确保这些变量是全局的，以便在线程中访问
    config = Config()
    wcf = Wcf(debug=True)

    # 初始化
    db_config = {
        'host': config.MySql.get('host'),
        'user': config.MySql.get('user'),
        'password': config.MySql.get('password'),
        'db': config.MySql.get('database'),
        'charset': 'utf8mb4',
        'cursorclass': pymysql.cursors.DictCursor
    }

    # Create a connection pool
    # 确保只创建一次连接池
    db_pool = DBConnectionPool(db_config, max_connections=5)
    # 确保只创建一次DBUtils实例
    db_utils = DBUtils(db_pool)

    def handler(sig, frame):
        wcf.cleanup()  # 退出前清理环境
        db_pool.release_all()  # 释放所有连接
        exit(0)

    signal.signal(signal.SIGINT, handler)

    robot = Robot(config, wcf, chat_type)

    robot.LOG.info(f"WeChatRobot【{__version__}】成功启动···")
    # 初始化群聊
    #init_group_info(robot)
    # 用于mysql
    init_group_info_mysql(robot,db_utils)

    # 机器人启动发送测试消息
    robot.sendTextMsg("机器人启动成功！", "filehelper")

    # 接收消息
    # robot.enableRecvMsg()     # 可能会丢消息？
    robot.enableReceivingMsg()  # 加队列
    # 每天 8 点发送天气预报
    # robot.onEveryTime("08:00", weather_report, robot=robot)
    # 每天 7 点初始化群聊
    robot.onEveryTime("07:00", init_group_info_mysql, robot=robot)

    #robot.onEverySeconds(80, get_mj_info, robot=robot)
    # robot.onEveryTime("07:10", init_group_info_mysql(robot,db_utils), robot=robot)

    # 每天 8:30 发送新闻
    # robot.onEveryTime("08:30", robot.newsReport)

    # 每天 18:00 提醒发日报周报月报
    #  robot.onEveryTime("18:00", ReportReminder.remind, robot=robot)
    # check_duolingo(robot, db_utils)
    # 每天 23:00 提醒 签到详情
    robot.onEveryTime("21:10", check_duolingo(robot, db_utils), robot=robot)

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
