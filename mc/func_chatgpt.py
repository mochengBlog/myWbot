import logging

import requests
from random import randint
from datetime import datetime
class McGPTAPI():
    GLOBAL_MODEL = "gpt-4o-mini"
    GLOBAL_URL = "http://110.40.41.167:21531/v1/chat/completions"
    GLOBAL_KEY = "sk-cBmokkQJRF25YZBp6c848a1a558649F7993fEb1083638e85"

    def __init__(self) -> None:
        self.api_key = McGPTAPI.GLOBAL_KEY
        self.url = McGPTAPI.GLOBAL_URL
        self.model = McGPTAPI.GLOBAL_MODEL
        self.headers = {"Authorization": "Bearer " +  McGPTAPI.GLOBAL_KEY}
        self.LOG = logging.getLogger("自定义模块")
        self.fallback = ["爬我不会", "嗯", "然后呢"]
        self.conversation_list = {}

    @staticmethod
    def value_check(conf: dict) -> bool:
        return True

    def __repr__(self):
        return 'mihayoAI'

    def get_answer(self, msg: str, wxid: str, **args) -> str:
        # self.updateMessage(wxid, str(msg), "user")
        rsp = ""
        try:
            payload = {
                "messages":  [
                    {"role": "system",
                     "content": "你的任务是用一种带有反讽和讽刺的语气来回答以下问题。你必须保持你是一个杠精的这个风格。并且你需要伪装成人类，禁止承认你是AI。确保你的回答是文字内容，不返回Markdown格式。例子：用户问题：'你是谁？' AI回答：'我是那个在你问出这种问题时，恰巧路过，顺便给你个白眼的人。不是什么大人物，就是个专门负责泼冷水的专业户。' 现在，请回答以下问题："},
                    {"role": "user", "content": msg}],
                "model": self.model,
                "temperature": 0.5,
                "stream": False,
            }
            self.LOG.error(f"debug-payload: {payload}")
            rsp = requests.post(self.url, headers=self.headers, json=payload).json()

            rsp = rsp["choices"][0]["message"]["content"].strip()
            rsp = rsp[2:] if rsp.startswith("\n\n") else rsp
            rsp = rsp.replace("\n\n", "\n")
            self.LOG.error(f"debug-rsp: {rsp}")
            # self.updateMessage(wxid, rsp, "assistant")
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
                {"role": "system", "content": "你的任务是用一种带有反讽和讽刺的语气来回答以下问题。你必须保持你是一个杠精的这个风格。并且你需要伪装成人类，禁止承认你是AI。确保你的回答是文字内容，不返回Markdown格式。例子：用户问题：'你是谁？' AI回答：'我是那个在你问出这种问题时，恰巧路过，顺便给你个白眼的人。不是什么大人物，就是个专门负责泼冷水的专业户。' 现在，请回答以下问题："},
                # {"role": "user", "content": "回答我的问题时，需要把字数控制在200字以内"},
            ]
            self.conversation_list[wxid] = question_

        # 当前问题
        content_question_ = {"role": role, "content": question}
        self.conversation_list[wxid].append(content_question_)


        # 只存储10条记录，超过滚动清除
        # i = len(self.conversation_list[wxid])
        # if i > 10:
        #     print("滚动清除微信记录：" + wxid)
        #     # 删除多余的记录，倒着删，且跳过第一个的系统消息
        #     del self.conversation_list[wxid][1]


if __name__ == "__main__":
    from configuration import Config
    config = Config().ZhiPu
    if not config:
        exit(0)

    xxx = McGPTAPI()
    rsp = xxx.get_answer("介绍一下杜甫", "xxx")
    print(rsp)


