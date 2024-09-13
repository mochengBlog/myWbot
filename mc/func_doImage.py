import fal_client
import os
import time
import random
import requests
import json


def get_response(prompt: str) -> str:
    os.environ["FAL_KEY"] = "53a7ceb7-a92e-4a24-9891-3fa6f8fbe2c5:41009f91640bc7f14f7e3fb70dea5bca"
    handler = fal_client.submit(
        "fal-ai/flux/dev",
        arguments={
            "seed": 9849598,
            "prompt": prompt,
            "image_size": "portrait_16_9",
            "num_images": 1,
            "guidance_scale": 3,
            "num_inference_steps": 20,
        },
    )

    result = handler.get()
    imageUrl = result.get("images")[0]["url"]
    return imageUrl


def get_image_path(prompt: str) -> str:
    try:
        getUrl = get_response(prompt)

        # 生成文件名
        timestamp = str(int(time.time()))
        random_num = str(random.randint(10000, 99999))
        file_name = f"{timestamp}_{random_num}.png"

        # 设置保存图片的路径
        user_desktop = os.path.join(os.path.expanduser("~"), "Desktop", "temp")
        save_path = os.path.join(user_desktop, file_name)

        # 确保 temp 文件夹存在
        if not os.path.exists(user_desktop):
            os.makedirs(user_desktop)

        # 下载并保存图片
        try:
            response = requests.get(getUrl)
            response.raise_for_status()
            with open(save_path, "wb") as f:
                f.write(response.content)
            print(f"图片已下载到: {save_path}")
        except Exception as e:
            print(f"下载图片时发生错误: {e}")
        return save_path

    except Exception as e:
        print(f"处理图片时发生错误: {e}")


def get_image_path_by_mj(prompt: str):
    try:
        url = "https://ephone.ai/mj/submit/imagine"
        payload = json.dumps({
            "prompt": prompt
        })
        headers = {
            'Authorization': 'sk-dSkpzziNCgohLR1uEe29001aB6Ef4bD4Bc84228d18D7E445',
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        # 解析 JSON 数据
        data = response.json()
        print(data)
        # 处理数据
        return response
    except Exception as e:
        print(f"处理图片时发生错误: {e}")


def get_task_process(taskId: str) -> str:
    try:

        url = "https://ephone.ai/mj/task/" + taskId + "/fetch"
        payload = {}
        headers = {
            'Authorization': 'sk-dSkpzziNCgohLR1uEe29001aB6Ef4bD4Bc84228d18D7E445',
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        # 解析 JSON 数据
        return response

    except Exception as e:
        print(f"处理图片时发生错误: {e}")


if __name__ == '__main__':
    # url = get_image_path_by_mj(" Plush toy design, cute plush animal toys, Nordic design, minimalist design, Disney style, product design, plush, cute, creative, practical, simple, natural plush, soft and delicate, extremely rich hidden details of plush texture, white background, Blender software tool, 8K, high definition, ultimate detail, high detail, HD, high quality, masterpiece, masterwork, ultra-high definition, high precision, full of vitality, heart-healing, dreamy plush texture, anime style. --ar 9:16 --stylize 1000")

    url = get_task_process('1726219522652629')
    print(url)
    # response = requests.get("https://fal.media/files/lion/dvMGO_x0jqo7DrNjpM7Ui.png")
    # response.raise_for_status()
    # with open("save_path", "wb") as f:
    #     f.write(response.content)
