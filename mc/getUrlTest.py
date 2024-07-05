import requests
import json
from wcferry import Wcf

receivers = ["filehelper"]


def get_weather_api() -> str:
    url = "https://hm.suol.cc/API/tq.php?msg=%E5%8C%97%E4%BA%AC&n=1"
    response = requests.get(url)
    return response.text


def test_send_image() -> str:
    try:
        response = requests.get("https://api.lolimi.cn/API/meinv/api.php")
        data = response.json()

        image_url = data["data"]["image"]

        return "http://img5.adesk.com/60ede5c9e7bce736620aadc1?sign=6c72d32bf970d85ffdc71c39582897ea&t=6687a872.jpg"

    except Exception as e:
        print(f"处理图片时发生错误: {e}")


def test_send_audio() -> None:
    Wcf.send_image()


if __name__ == '__main__':
    print(test_send_image())
    # print(get_weather_api())
