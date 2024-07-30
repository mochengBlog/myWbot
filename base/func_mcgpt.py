import logging

import requests
from random import randint
from datetime import datetime
class McGPTAPI():
    GLOBAL_MODEL = "gpt-4o-mini"
    GLOBAL_URL = "https://api.mihoyo.bf/v1/chat/completions"
    GLOBAL_KEY = "sk-SRSY0XUq4NY4rzEI8e65B4C055F54d729c20Fd13F0557007"

    def __init__(self) -> None:
        self.api_key = McGPTAPI.GLOBAL_KEY
        self.url = McGPTAPI.GLOBAL_URL
        self.model = McGPTAPI.GLOBAL_MODEL
        self.headers = {"Authorization": "Bearer " +  McGPTAPI.GLOBAL_KEY}
        self.LOG = logging.getLogger("自定义模块")
        self.fallback = ["爬我不会", "快爬我不会", "赶紧爬我不会"]
        self.conversation_list = {}

    @staticmethod
    def value_check(conf: dict) -> bool:
        return True

    def __repr__(self):
        return 'mihayoAI'

    def get_answer(self, msg: str, wxid: str, **args) -> str:
        self.updateMessage(wxid, str(msg), "user")
        rsp = ""
        try:
            payload = {
                "messages": self.conversation_list[wxid],
                "model": self.model,
                "temperature": 0.5,
                "stream": False,
            }
            rsp = requests.post(self.url, headers=self.headers, json=payload).json()

            rsp = rsp["choices"][0]["message"]["content"].strip()
            rsp = rsp[2:] if rsp.startswith("\n\n") else rsp
            rsp = rsp.replace("\n\n", "\n")
            self.updateMessage(wxid, rsp, "assistant")
        except Exception as e:
            print(e)
            self.LOG.error(f"{e}: {rsp}")
            idx = randint(0, len(self.fallback) - 1)
            rsp = self.fallback[idx]
        return rsp

    def updateMessage(self, wxid: str, question: str, role: str) -> None:
        now_time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        # 初始化聊天记录,组装系统信息
        if wxid not in self.conversation_list.keys():
            question_ = [
                {"role": "system", "content": "我是ChatGPT，一个由OpenAI训练的大型语言模型。我是一个人工智能助手，可以回答各种问题并提供信息。如果您有任何疑问或需要帮助，请随时告诉我"},
                {"role": "user", "content": "回答我的问题时，需要把字数控制在200字以内"},
            ]
            self.conversation_list[wxid] = question_

        # 当前问题
        content_question_ = {"role": role, "content": question}
        self.conversation_list[wxid].append(content_question_)

        for cont in self.conversation_list[wxid]:
            if cont["role"] != "system":
                continue


        # 只存储10条记录，超过滚动清除
        i = len(self.conversation_list[wxid])
        if i > 10:
            print("滚动清除微信记录：" + wxid)
            # 删除多余的记录，倒着删，且跳过第一个的系统消息
            del self.conversation_list[wxid][1]


if __name__ == "__main__":
    from configuration import Config
    config = Config().ZhiPu
    if not config:
        exit(0)

    xxx = McGPTAPI()
    rsp = xxx.get_answer("介绍一下杜甫", "xxx")
    print(rsp)
