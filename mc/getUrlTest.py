import requests
import json
import os
import time
import random
from wcferry import Wcf

receivers = ["filehelper"]


def get_weather_api() -> str:
    url = "https://hm.suol.cc/API/tq.php?msg=%E5%8C%97%E4%BA%AC&n=1"
    response = requests.get(url)
    return response.text


def test_send_image() -> str:
    try:
        # 获取图片 URL
        response = requests.get("https://api.lolimi.cn/API/meinv/api.php")
        data = response.json()
        image_url = data["data"]["image"]

        # 生成文件名
        timestamp = str(int(time.time()))
        random_num = str(random.randint(10000, 99999))
        file_name = f"{timestamp}_{random_num}.jpg"

        # 设置保存图片的路径
        user_desktop = os.path.join(os.path.expanduser("~"), "Desktop", "temp")
        save_path = os.path.join(user_desktop, file_name)

        # 确保 temp 文件夹存在
        if not os.path.exists(user_desktop):
            os.makedirs(user_desktop)

        # 下载并保存图片
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            with open(save_path, "wb") as f:
                f.write(response.content)
            print(f"图片已下载到: {save_path}")
        except Exception as e:
            print(f"下载图片时发生错误: {e}")
        return save_path

    except Exception as e:
        print(f"处理图片时发生错误: {e}")


def test_send_audio() -> None:
    Wcf.send_image()


if __name__ == '__main__':
    print(test_send_image())
    # print(get_weather_api())
