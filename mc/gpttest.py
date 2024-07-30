import requests

url = 'https://api.mihoyo.bf/v1/chat/completions'
headers = {
    'authorization': 'Bearer sk-SRSY0XUq4NY4rzEI8e65B4C055F54d729c20Fd13F0557007',
}

data = {
    "messages": [
        {"role":"user","content":"介绍一下李白"},
        # {"role":"system","content":"回答字符不能超过1000字符，不要解释、不要标点、不要语气词、不要多余文本，不要加粗"}
    ],
    "stream": False,
    "model": "gpt-4o-mini",
    "temperature": 0.5,
    "presence_penalty": 0,
    "frequency_penalty": 0,
    "top_p": 1
}

response = requests.post(url, headers=headers, json=data)
print(response.json())