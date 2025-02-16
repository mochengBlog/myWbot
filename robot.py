# -*- coding: utf-8 -*-
import datetime
import logging
import re
import time
import requests
import xml.etree.ElementTree as ET

import wcferry

import mc.getUrlTest as McTest
import mc.func_doImage as doImage
from queue import Empty
from threading import Thread
from base.func_zhipu import ZhiPu
from base.func_mcgpt import McGPTAPI

from wcferry import Wcf, WxMsg

from base.func_bard import BardAssistant
from base.func_chatglm import ChatGLM
from base.func_chatgpt import ChatGPT
from base.func_chengyu import cy
from base.func_news import News
from base.func_tigerbot import TigerBot
from base.func_xinghuo_web import XinghuoWeb
from configuration import Config
from constants import ChatType
from job_mgmt import Job
import pymysql

__version__ = "39.0.10.1"

from mc import groupSign
from db.pySql import DBUtils, DBConnectionPool
from mc.dida365_api import sendDIDA365Email
from mc.Iching import IChing
from mc.duo_lin_guo import check_duolingo_status


class Robot(Job):
    """个性化自己的机器人
    """

    def __init__(self, config: Config, wcf: Wcf, chat_type: int) -> None:
        self.wcf = wcf
        self.config = config
        self.LOG = logging.getLogger("Robot")
        self.wxid = self.wcf.get_self_wxid()
        self.allContacts = self.getAllContacts()
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
        self.dbUtils = DBUtils(db_pool)

        if ChatType.is_in_chat_types(chat_type):
            if chat_type == ChatType.TIGER_BOT.value and TigerBot.value_check(self.config.TIGERBOT):
                self.chat = TigerBot(self.config.TIGERBOT)
            elif chat_type == ChatType.CHATGPT.value and ChatGPT.value_check(self.config.CHATGPT):
                self.chat = ChatGPT(self.config.CHATGPT)
            elif chat_type == ChatType.XINGHUO_WEB.value and XinghuoWeb.value_check(self.config.XINGHUO_WEB):
                self.chat = XinghuoWeb(self.config.XINGHUO_WEB)
            elif chat_type == ChatType.CHATGLM.value and ChatGLM.value_check(self.config.CHATGLM):
                self.chat = ChatGLM(self.config.CHATGLM)
            elif chat_type == ChatType.BardAssistant.value and BardAssistant.value_check(self.config.BardAssistant):
                self.chat = BardAssistant(self.config.BardAssistant)
            elif chat_type == ChatType.ZhiPu.value and ZhiPu.value_check(self.config.ZhiPu):
                self.chat = ZhiPu(self.config.ZhiPu)
            elif chat_type == ChatType.McGPTAPI.value:
                self.chat = McGPTAPI()
            else:
                self.LOG.warning("未配置模型")
                self.chat = McGPTAPI()
        else:
            if TigerBot.value_check(self.config.TIGERBOT):
                self.chat = TigerBot(self.config.TIGERBOT)
            elif ChatGPT.value_check(self.config.CHATGPT):
                self.chat = ChatGPT(self.config.CHATGPT)
            elif XinghuoWeb.value_check(self.config.XINGHUO_WEB):
                self.chat = XinghuoWeb(self.config.XINGHUO_WEB)
            elif ChatGLM.value_check(self.config.CHATGLM):
                self.chat = ChatGLM(self.config.CHATGLM)
            elif BardAssistant.value_check(self.config.BardAssistant):
                self.chat = BardAssistant(self.config.BardAssistant)
            elif ZhiPu.value_check(self.config.ZhiPu):
                self.chat = ZhiPu(self.config.ZhiPu)
            else:
                self.LOG.warning("未配置模型,默认走自定义模型")
                self.chat = McGPTAPI()

        self.LOG.info(f"已选择: {self.chat}")

    @staticmethod
    def value_check(args: dict) -> bool:
        if args:
            return all(value is not None for key, value in args.items() if key != 'proxy')
        return False

    def toAt(self, msg: WxMsg) -> bool:
        """处理被 @ 消息
        :param msg: 微信消息结构
        :return: 处理状态，`True` 成功，`False` 失败
        """

        return self.toChitchat(msg)

    def toChengyu(self, msg: WxMsg) -> bool:
        """
        处理成语查询/接龙消息
        :param msg: 微信消息结构
        :return: 处理状态，`True` 成功，`False` 失败
        """
        status = False
        texts = re.findall(r"^([#|?|？])(.*)$", msg.content)
        # [('#', '天天向上')]
        if texts:
            flag = texts[0][0]
            text = texts[0][1]
            if flag == "#":  # 接龙
                if cy.isChengyu(text):
                    rsp = cy.getNext(text)
                    if rsp:
                        self.sendTextMsg(rsp, msg.roomid)
                        status = True
            elif flag in ["?", "？"]:  # 查词
                if cy.isChengyu(text):
                    rsp = cy.getMeaning(text)
                    if rsp:
                        self.sendTextMsg(rsp, msg.roomid)
                        status = True

        return status

    def toChitchat(self, msg: WxMsg) -> bool:
        """闲聊，接入 ChatGPT
        """
        if not self.chat:  # 没接 ChatGPT，固定回复
            rsp = "你@我干嘛？"
        else:  # 接了 ChatGPT，智能回复
            q = re.sub(r"@.*?[\u2005|\s]", "", msg.content).replace(" ", "")
            rsp = self.chat.get_answer(q, (msg.roomid if msg.from_group() else msg.sender))

        if rsp:
            if msg.from_group():
                self.sendTextMsg(rsp, msg.roomid, msg.sender)
            else:
                self.sendTextMsg(rsp, msg.sender)

            return True
        else:
            self.LOG.error(f"无法从 ChatGPT 获得答案")
            return False

    def processMsg(self, msg: WxMsg) -> None:
        """当接收到消息的时候，会调用本方法。如果不实现本方法，则打印原始消息。
        此处可进行自定义发送的内容,如通过 msg.content 关键字自动获取当前天气信息，并发送到对应的群组@发送者
        群号：msg.roomid  微信ID：msg.sender  消息内容：msg.content
        content = "xx天气信息为："
        receivers = msg.roomid
        self.sendTextMsg(content, receivers, msg.sender)
        """
        content = msg.content
        # 群聊消息
        if msg.from_group():
            # if msg.type == 1: # 如果是文本
            #     # 保存群聊消息
            #     self.dbUtils.insert('messages',
            #                         {'room_id': msg.roomid, 'sender_id': msg.sender, 'chat_id': msg.id, 'message': content,'message_type': 1,
            #                          'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

            # if msg.type == 49:  # 带有引用的文本消息（这种类型下 StrContent 为空，发送和引用的内容均在 CompressContent 中）
            # if msg.type == 49:  # 合并转发的聊天记录，CompressContent 中有详细聊天记录，BytesExtra 中有图片视频等的缓存
            #if msg.type == 3:   # 如果是图片把图片上传到图床

            # 如果在群里被 @
            if msg.roomid not in self.config.GROUPS:  # 不在配置的响应的群列表里，忽略
                return
            if msg.is_at(self.wxid):  # 被@
                self.toAt(msg)

            else:  # 其他消息
                if "#占卜" in content:
                    content = content.replace("#占卜", "")
                    if not content.strip():
                        # 请输入占卜内容
                        print("字符串为空或仅包含空格")
                        self.sendTextMsg("请输入占卜问题(例如：#占卜 今天我能发财吗?)", msg.roomid)
                    else:
                        #开始算卦
                        self.sendTextMsg("正在进行<蓍草占卜>", msg.roomid)
                        bengua_info, biangua_info = IChing.giet_guaming_info()
                        bengua = f"本卦：{bengua_info['name']}\n卦辞：{bengua_info['text']}\n卦象：{bengua_info['interpretation']}"
                        biangua = f"变卦：{biangua_info['name']}\n卦辞：{biangua_info['text']}\n卦象：{biangua_info['interpretation']}"
                        self.sendTextMsg(bengua, msg.roomid)
                        self.sendTextMsg(biangua, msg.roomid)
                        self.sendTextMsg("大师解读正在解读.....", msg.roomid)
                        rsp = self.chat.get_answer_by_rompt(bengua + biangua, content, 'iching.txt')
                        if rsp:
                            if msg.from_group():
                                self.sendTextMsg(rsp, msg.roomid, msg.sender)
                            else:
                                self.sendTextMsg(rsp, msg.sender)

                #  添加到滴答清单
                if "#todo" in content:
                    content = content.replace("#todo", "")
                    # 添加到滴答清单 content  用 ｜分割主题和info
                    info = content.split("｜")
                    sendDIDA365Email(info[0], info[1], self.config.MySql.get('mail_pass'));
                if "#画画" in content:
                    content = content.replace("#画画", "")
                    self.sendImage(doImage.get_image_path(content), msg.roomid)
                if "#mj" in content:
                    content = content.replace("#mj", "")
                    self.sendTextMsg("正在提交任务", msg.roomid, msg.sender)
                    result = doImage.get_image_path_by_mj(content).json()
                    if "error" in result:
                        self.sendTextMsg("充点钱啊 死鬼", msg.roomid, msg.sender)
                    if result['code'] == 1:
                        self.sendTextMsg("提交成功,请等待(40-120s),taskId为" + result['result'] + "", msg.roomid,
                                         msg.sender)
                        # 数据存储在sqllite中
                        self.dbUtils.insert('mj_info',
                                            {'room_id': msg.roomid,
                                             'task_id': result['result'],
                                             'sender_id': msg.sender,
                                             'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
                    elif result['code'] == 22:
                        self.dbUtils.insert('mj_info',
                                            {'room_id': msg.roomid,
                                             'task_id': result['result'],
                                             'sender_id': msg.sender,
                                             'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
                        self.sendTextMsg(result['result'] + "排队中，请等待", msg.roomid, msg.sender)
                    else:
                        self.LOG.info(result)  # 打印信息
                        self.sendTextMsg("提交失败,自己改bug", msg.roomid, msg.sender)
                if "#壁纸" in content:
                    if content == "#壁纸":
                        self.sendTextMsg("请输入壁纸关键字:" + McTest.get_type_enum(), msg.roomid)
                        return
                    self.sendImage(McTest.test_send_image(content), msg.roomid)
                if "#签到规则" in content:
                    self.sendTextMsg("签到规则为:发送 #签到 即可签到,2点前算作昨天 ; 发送 #补签昨天 即可补签前一日",
                                     msg.roomid)
                if "#签到" in content:
                    # groupSign.insert(msg.roomid, msg.sender, "已签到")
                    self.dbUtils.SignInsert(msg.roomid, msg.sender, 1)
                    self.sendTextMsg("签到成功，明天也要努力呦！",msg.roomid, msg.sender)
                if "#多邻国启动" in content:
                    user_map = self.dbUtils.getDuoLinGuoUser()
                    status_dict = check_duolingo_status(user_map)
                    # 写入签到结果
                    self.dbUtils.DuoLinGuoSignInsert(status_dict, "43541810338@chatroom")
                    self.sendTextMsg("多邻国打卡结果", "43541810338@chatroom")
                    # 将所有用户的打卡状态合并到一个字符串中
                    status_lines = []
                    for name, status in status_dict.items():
                        if status.get("status") == "error":
                            status_lines.append(f"{name}: {status['message']}")
                        else:
                            status_lines.append(f"{name} {status['status']}")

                    # 使用换行符连接所有状态信息并打印
                    self.sendTextMsg('\n'.join(status_lines), "43541810338@chatroom")

                if "#补签" in content:
                    if "昨天" in content or "前天" in content:
                        self.dbUtils.SignInsertBQ(msg.roomid, msg.sender, 1, content)
                        self.sendTextMsg("下不为例！",
                                         msg.roomid, msg.sender)
                    else:
                        self.sendTextMsg("暂不支持其他天补签", msg.roomid)
                if content == "#学习一个知识点":
                    self.sendImage(McTest.test_send_image(), msg.roomid)
                if content == "#抽签":
                    self.sendChouq(McTest.test_Chouq(), msg)
                else:
                    self.toChengyu(msg)

            return  # 处理完群聊信息，后面就不需要处理了

        # 非群聊信息，按消息类型进行处理
        if msg.type == 37:  # 好友请求
            self.autoAcceptFriendRequest(msg)

        elif msg.type == 10000:  # 系统信息
            self.sayHiToNewFriend(msg)

        elif msg.type == 0x01:  # 文本消息

            # 让配置加载更灵活，自己可以更新配置。也可以利用定时任务更新。
            if msg.from_self():
                if msg.content == "^更新$":
                    self.config.reload()
                    self.LOG.info("已更新")
            else:
                self.toChitchat(msg)  # 闲聊

    def onMsg(self, msg: WxMsg) -> int:
        try:
            self.LOG.info(msg)  # 打印信息
            self.processMsg(msg)
        except Exception as e:
            self.LOG.error(e)

        return 0

    def enableRecvMsg(self) -> None:
        self.wcf.enable_recv_msg(self.onMsg)

    def enableReceivingMsg(self) -> None:
        def innerProcessMsg(wcf: Wcf):
            while wcf.is_receiving_msg():
                try:
                    msg = wcf.get_msg()
                    self.LOG.info(msg)
                    self.processMsg(msg)
                except Empty:
                    continue  # Empty message
                except Exception as e:
                    self.LOG.error(f"Receiving message error: {e}")

        self.wcf.enable_receiving_msg()
        Thread(target=innerProcessMsg, name="GetMessage", args=(self.wcf,), daemon=True).start()

    def sendTextMsg(self, msg: str, receiver: str, at_list: str = "") -> None:
        """ 发送消息
        :param msg: 消息字符串
        :param receiver: 接收人wxid或者群id
        :param at_list: 要@的wxid, @所有人的wxid为：notify@all
        """
        # msg 中需要有 @ 名单中一样数量的 @
        ats = ""
        if at_list:
            if at_list == "notify@all":  # @所有人
                ats = " @所有人"
            else:
                wxids = at_list.split(",")
                for wxid in wxids:
                    # 根据 wxid 查找群昵称
                    ats += f" @{self.wcf.get_alias_in_chatroom(wxid, receiver)}"

        # {msg}{ats} 表示要发送的消息内容后面紧跟@，例如 北京天气情况为：xxx @张三
        if ats == "":
            self.LOG.info(f"To {receiver}: {msg}")
            self.wcf.send_text(f"{msg}", receiver, at_list)
        else:
            self.LOG.info(f"To {receiver}: {ats}\r{msg}")
            self.wcf.send_text(f"{ats}\n\n{msg}", receiver, at_list)

    def sendImage(self, filePath: str, receiver: str) -> None:
        """ 发送消息
        :param filePath :  图片路径
        :param receiver: 接收人wxid或者群id
        """
        self.LOG.info(f"获取图片地址 {filePath}")
        self.wcf.send_image(filePath, receiver)

    def sendChouq(self, context: str, msg: WxMsg) -> None:
        """ 发送消息
        :param context :  结果
        :param msg:
        """
        self.sendTextMsg(context, msg.roomid, msg.sender)

    def getRoomInfo(self, roomid: str) -> dict:
        """ 发送消息
        :param msg:
        """
        # 获取所有群成员及名称
        return self.wcf.get_chatroom_members(roomid)

    def getRoomDataInfo(self, roomid: str) -> dict:
        """ 发送消息
        :param msg:
        """
        # 获取所有群成员及名称
        return self.wcf.get_chatroom_data(roomid)

    def getAllContacts(self) -> dict:
        """
        获取联系人（包括好友、公众号、服务号、群成员……）
        格式: {"wxid": "NickName"}
        """
        contacts = self.wcf.query_sql("MicroMsg.db", "SELECT UserName, NickName FROM Contact;")
        return {contact["UserName"]: contact["NickName"] for contact in contacts}

    def keepRunningAndBlockProcess(self) -> None:
        """
        保持机器人运行，不让进程退出
        """
        while True:
            self.runPendingJobs()
            time.sleep(1)

    def autoAcceptFriendRequest(self, msg: WxMsg) -> None:
        try:
            xml = ET.fromstring(msg.content)
            v3 = xml.attrib["encryptusername"]
            v4 = xml.attrib["ticket"]
            scene = int(xml.attrib["scene"])
            self.wcf.accept_new_friend(v3, v4, scene)

        except Exception as e:
            self.LOG.error(f"同意好友出错：{e}")

    def sayHiToNewFriend(self, msg: WxMsg) -> None:
        nickName = re.findall(r"你已添加了(.*)，现在可以开始聊天了。", msg.content)
        if nickName:
            # 添加了好友，更新好友列表
            self.allContacts[msg.sender] = nickName[0]
            self.sendTextMsg(f"Hi {nickName[0]}，我自动通过了你的好友请求。", msg.sender)

    def newsReport(self) -> None:
        receivers = self.config.NEWS
        if not receivers:
            return

        news = News().get_important_news()
        for r in receivers:
            self.sendTextMsg(news, r)

    def sendXml(self) -> None:
        self.wcf.send_xml()

    def check_duolingo(self) -> None:
        user_map = self.dbUtils.getDuoLinGuoUser()
        status_dict = check_duolingo_status(user_map)

        # 将所有用户的打卡状态合并到一个字符串中
        status_lines = []
        for name, status in status_dict.items():
            if status.get("status") == "error":
                status_lines.append(f"{name}: {status['message']}")
            else:
                status_lines.append(f"{name} {status['status']}")

        self.dbUtils.DuoLinGuoSignInsert(status_dict, "43541810338@chatroom")

        # 使用换行符连接所有状态信息并打印
        self.sendTextMsg("多邻国打卡结果", "43541810338@chatroom")
        self.sendTextMsg('\n'.join(status_lines), "43541810338@chatroom")

    def warn_duolingo(self) -> None:
        user_map = self.dbUtils.getDuoLinGuoUser()
        # 使用换行符连接所有状态信息并打印
        self.sendTextMsg("没打卡的赶紧了", "43541810338@chatroom")
    def init_group_info_mysql(self) -> None:
        self.dbUtils.execute_query("truncate table room_info")
        receivers = self.dbUtils.execute_query("select room_id from messages group by room_id ");
        for r in receivers:
            # 获取字典r的值
            r = r['room_id']
            group_info = self.getRoomInfo(r)
            # 初始化群聊 {'wxid_1538135380812': '莫城', 'wxid_ej6qv9p6r6bg22': '乌苏里江畔', 'wxid_ytllv9po50bj12': 'CikL.'}
            for wxid, name in group_info.items():
                #查询该room_id 下的wxid是否存，若存在 判断name是否相等
                self.dbUtils.insert("room_info", {"room_id": r, "vxid": wxid, "name": name})