import datetime
import sqlite3
import db.dbconn as dbconn


def query_by_date(table, date):
    conn = dbconn.get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM " + table + " where date = ? ", (date,))
    rows = c.fetchall()
    conn.close()
    #生成本地txt文件
    with open('test.txt', 'w', encoding='utf-8') as f:
        for row in rows:
            f.write(str(row) + '\n')
    return rows

if __name__ == '__main__':
    query_by_date('group_sign', '2024-07-17')
