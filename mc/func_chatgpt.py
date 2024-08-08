import logging
from datetime import datetime

import httpx
from openai import APIConnectionError, APIError, AuthenticationError, OpenAI


def get_response():
    client = OpenAI(api_key="sk-gbBE1mOPTTA6OdgU5a28De5cE6744b1d88C750C00397B7A1",
                    base_url="https://api.freegpt.art/v1/chat/completions",
                    http_client=httpx.Client(proxy="https://api.freegpt.art")
                    )
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": "你是谁"},
            {"role": "assistant",
             "content": "我是ChatGPT，一个由OpenAI训练的大型语言模型。我是一个人工智能助手，可以回答各种问题并提供信息。如果您有任何疑问或需要帮助，请随时告诉我。"},
            {"role": "user",
             "content": "使用四到五个字直接返回这句话的简要主题，不要解释、不要标点、不要语气词、不要多余文本，不要加粗，如果没有主题，请直接返回闲聊"}
        ],
        temperature=0.2
    )
    print(completion.model_dump_json())


if __name__ == '__main__':
    get_response()

