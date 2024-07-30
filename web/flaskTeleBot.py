from flask import Flask, request
from threading import Thread
import telebot
from flask_sqlalchemy import SQLAlchemy
import atexit

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://root:admin@localhost/test'
db = SQLAlchemy(app)

class Message(db.Model):
    # 定义数据模型
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255))
    status = db.Column(db.String(255))
    url = db.Column(db.String(255))
    mes_type = db.Column(db.String(255))
    file_path = db.Column(db.String(255))

@app.route('/save', methods=['GET', 'POST'])
def save():
    # 实现 save操作
    if request.method == 'POST':
        text = request.form['text']
        status = request.form['status']
        url = request.form['url']
        mes_type = request.form['mes_type']
        file_path = request.form['file_path']
        message = Message(text=text, status=status, url=url, mes_type=mes_type, file_path=file_path)
        db.session.add(message)
        db.session.commit()
    return 'OK'

@app.route('/messages/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def message(id):
    # 实现 CRUD 操作
    pass

def cleanup():
    """
    程序退出时执行的清理操作
    """
    db.session.close()
    db.engine.dispose()
    print("程序已优雅地退出!")

atexit.register(cleanup)

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
    with app.app_context():
        db.create_all()
    app.run(debug=True)
    # 运行 Flask 应用