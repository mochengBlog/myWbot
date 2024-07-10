import json
import os

import telebot
import sqlite3


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


# 创建表格
def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS message
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, text TEXT, status TEXT
                  url TEXT,mes_type TEXT
                 )''')
    conn.commit()
    conn.close()


bot = telebot.TeleBot('6977364720:AAFNH1GGTfuk6EMQdTyY_k0catMJHfyCxEU')


@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")

@bot.message_handler(content_types=['text','forwarded_message'])
def echo_all(message):
    print(message)

    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT INTO message (mes_type,text) VALUES (?,?)", ("text",message.text))
    conn.commit()
    conn.close()
    bot.reply_to(message, message.text)

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    print(message)
    message.caption

    file_id = message.photo[-1].file_id
    bot.get_file_url()
    # 下载并处理图片

@bot.message_handler(content_types=['video'])
def handle_video(message):
    print(message)
    file_id = message.video.file_id
    # 下载并处理视频

if __name__ == '__main__':
    init_db()
    bot.infinity_polling();

