import os

import telebot


bot = telebot.TeleBot('6977364720:AAFNH1GGTfuk6EMQdTyY_k0catMJHfyCxEU')

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")

@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    print(message)
    print(message.text)
    bot.reply_to(message, message.text)

bot.infinity_polling()
