from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# 数据库连接函数
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# 创建表格
def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT)''')
    conn.commit()
    conn.close()

# 首页路由 - 显示用户列表
@app.route('/')
def index():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    return render_template('index.html', users=users)

# 创建用户路由
@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("INSERT INTO users (name, email) VALUES (?, ?)", (name, email))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('create.html')

# 更新用户路由
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (id,)).fetchone()
    conn.close()

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("UPDATE users SET name = ?, email = ? WHERE id = ?", (name, email, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    return render_template('update.html', user=user)

# 删除用户路由
@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)