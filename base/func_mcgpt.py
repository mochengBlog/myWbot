import logging

import requests
from random import randint
from datetime import datetime


def load_prompt_from_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        return file.read().strip()
class McGPTAPI():
    GLOBAL_MODEL = "gpt-4o-mini"
    GLOBAL_URL = "https://api.ephone.ai/v1/chat/completions"
    GLOBAL_KEY = "sk-dSkpzziNCgohLR1uEe29001aB6Ef4bD4Bc84228d18D7E445"
    # GLOBAL_MODEL = "deepseek-reasoner"
    # GLOBAL_URL = "https://api.deepseek.com/v1/chat/completions"
    # GLOBAL_KEY = "sk-fb5cf227798d41cfa178f879c226a1cd"
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
        PROMPT_FILE_PATH = './fanfeng_prompt.txt'
        try:
            PROMPT = load_prompt_from_file(PROMPT_FILE_PATH)
        except Exception as e:
            logging.error(f"Failed to load prompt from file: {e}")
            PROMPT = "带入一个只有幼儿园文化的人的视角，与我进行对话：\n"  # 如果加载失败，使用默认值
        rsp = ""
        try:
            payload = {
                "messages": [
                    {"role": "user", "content": f"{PROMPT, msg}"}],
                "model": self.model,
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


    def get_answer_by_rompt(self, msg: str,question: str, prompt: str) -> str:
        # self.updateMessage(wxid, str(msg), "user")
        PROMPT_FILE_PATH = './'+prompt
        try:
            PROMPT = load_prompt_from_file(PROMPT_FILE_PATH)
        except Exception as e:
            logging.error(f"Failed to load prompt from file: {e}")
            PROMPT = "解读以下卦象,并回答问题回答不要超过100字：\n"  # 如果加载失败，使用默认值
        rsp = ""
        try:
            payload = {
                "messages": [
                    {"role": "user", "content": f"{PROMPT,question, msg}"}],
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
    rsp = xxx.get_answer("我非常深爱我的爷爷奶奶，他们已经去世了。我同样热爱未来世界和遥远的星辰。如果有一天，有一个机会摆在面前：我可以选择去未来和远方，抑或是过去与故土。我该怎么选择？如果我回到过去，我会遭遇什么？", "xxx")
    print(rsp)


