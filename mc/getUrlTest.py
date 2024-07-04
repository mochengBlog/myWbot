import requests


def get_weather_api() -> None:
    url = "https://hm.suol.cc/API/tq.php?msg=%E5%8C%97%E4%BA%AC&n=1"
    response = requests.get(url)
    return response.text


if __name__ == '__main__':
    print(get_weather_api())

