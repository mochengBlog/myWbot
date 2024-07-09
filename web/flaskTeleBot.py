from flask import Flask, request
from threading import Thread
import telebot

app = Flask(__name__)

# 假设你的 bot token 是 'YOUR_TOKEN'
TOKEN = 'YOUR_TOKEN'
bot = telebot.TeleBot('6977364720:AAFNH1GGTfuk6EMQdTyY_k0catMJHfyCxEU')


@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")


@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    print(message)
    print(message.text)
    bot.reply_to(message, message.text)


@app.route('/bot')
def test():
    bot.send_message(chat_id="1543260695", text="hellow 11")

    return 'OK'

@app.route('/ok')
def ok():
    return 'OK'


def start_bot():
    bot.infinity_polling()


if __name__ == '__main__':
    # 创建一个线程来运行 bot
    bot_thread = Thread(target=start_bot)
    bot_thread.daemon = True  # 设置为守护线程，这样主线程结束时，子线程也会结束
    bot_thread.start()

    # 运行 Flask 应用
    app.run()
