import fal_client
import os
import requests
import time
import random

def get_response(prompt: str ) -> str:
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

def get_image_path(prompt: str ) -> str:
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


if __name__ == '__main__':
    url = get_image_path("一个可爱的小狗在草坪上玩耍")
    print(url)
    # response = requests.get("https://fal.media/files/lion/dvMGO_x0jqo7DrNjpM7Ui.png")
    # response.raise_for_status()
    # with open("save_path", "wb") as f:
    #     f.write(response.content)