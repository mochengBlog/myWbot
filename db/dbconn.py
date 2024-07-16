import os
import sqlite3

def get_db_connection():
    # 获取当前脚本的路径
    current_path = os.path.dirname(os.path.abspath(__file__))

    # 构建数据库文件的完整路径
    db_path = os.path.join(current_path, "bot.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_group_info_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS group_info
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    rome_id TEXT,
                    vx_id TEXT,
                    name TEXT
                    )''')
    conn.commit()
    conn.close()


def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS group_sign
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                 room_id TEXT,
                 vx_id TEXT,
                 sign TEXT,
                 date TEXT
                 )''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_group_info_db()
    init_db()