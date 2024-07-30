import json
import os
import logging
import requests
import telebot
import sqlite3
import pymysql

logging.basicConfig(level=logging.WARNING)
# 或者针对特定的日志记录器
logging.getLogger('urllib3').setLevel(logging.WARNING)

conn = pymysql.connect(host='localhost', user='root', password='admin', db='telebot')
cursor = conn.cursor()

bot = telebot.TeleBot('6977364720:AAFNH1GGTfuk6EMQdTyY_k0catMJHfyCxEU')


@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")


@bot.message_handler(content_types=['text', 'forwarded_message'])
def echo_all(message):
    text = message.text
    #如果text有两个 /n 去掉一个/n
    # if text.find('\n') != -1:
    #     text = text[:text.find('\n')]
    # 检查消息是否包含链接预览选项
    # print(message.link_preview_options.url)
    text = text+"\n预览链接\n"+message.link_preview_options.url

    sql = "INSERT INTO bot_message (text, mes_type,status) VALUES (%s,'text','已保存')"
    values = (text)
    cursor.execute(sql, values)
    conn.commit()  # 提交更改


@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    # print(message)
    # 获取最高质量的照片文件
    photo_file = bot.get_file(message.photo[-1].file_id)

    # 下载照片文件
    downloaded_file = bot.download_file(photo_file.file_path)
    file_name = photo_file.file_unique_id
    # 保存路径
    save_path = "/Users/mocheng/Desktop/img/" + file_name + ".jpg"
    # 保存照片文件
    with open(save_path, "wb") as f:
        f.write(downloaded_file)

    print(message.caption)
    sql = "INSERT INTO bot_message (text, mes_type,file_path,status) VALUES (%s,'photo',%s,'已保存')"
    values = (message.caption, save_path)
    cursor.execute(sql, values)
    conn.commit()  # 提交更改



@bot.message_handler(content_types=['video'])
def handle_video(message):
    print(message)
    file_id = message.video.file_id
    # 下载并处理视频


def receive_file(message, bot, folder_path):
    if (message.audio != None): #audio类型文件
        file_id = message.audio.file_id
        file_name = message.audio.file_name
    elif (message.document != None): #document类型文件
        file_id = message.document.file_id
        file_name = message.document.file_name
    elif (message.video != None): #video类型文件
        file_id = message.video.file_id
        file_name = message.video.file_name
    elif (message.photo != None): #photo类型文件
        file_id = message.photo[-1].file_id #最大分辨率
        file_name = f'{message.date}.jpg'
    else:
        bot.send_message(message.chat.id, f"❗️ 发送的不是文件！")
        return
    download_url = bot.get_file_url(file_id)
    print(download_url)
    res = requests.get(download_url)
    with open(os.path.join(folder_path, file_name), 'wb') as f:
        f.write(res.content)

    # bot.send_message(message.chat.id, f"✅ 文件保存为{file_name}")

if __name__ == '__main__':
    # init_db()
    try:
        bot.infinity_polling();
    except Exception as e:
        print(1)
