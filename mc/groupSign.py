import sqlite3
import db.dbconn as dbconn


# 根据日期查询是否签到
def query_by_date(room_id,date):
    conn = dbconn.get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM group_sign where date = ? and sign = ?", (date, '已签到'))
    rows = c.fetchall()
    conn.close()
    return rows


def insert(room_id, vx_id, sign, date):
    conn = dbconn.get_db_connection()
    c = conn.cursor()
    # 查询是否已经存在
    c.execute("SELECT * FROM group_sign where rome_id = ? and vx_id = ? and date = ?", (room_id, vx_id , date))
    rows = c.fetchall()
    if len(rows) == 0:
        print("插入签到")
        c.execute("INSERT INTO group_sign (room_id,vx_id,sign,date) VALUES (?,?,?,?)", (room_id, vx_id, sign, date))
    else:
        print("更新签到")
    conn.commit()
    conn.close()

#初始化group_info表
def init_group_info(room_id, vx_id, name):
    conn = dbconn.get_db_connection()
    c = conn.cursor()
    #查询是否已经存在
    c.execute("SELECT * FROM group_info where rome_id = ? and vx_id = ? ", (room_id, vx_id))
    rows = c.fetchall()
    if len(rows) == 0:
        print("更新群信息")
        c.execute("INSERT INTO group_info (rome_id,vx_id,name) VALUES (?,?,?)", (room_id, vx_id, name))
    conn.commit()
    conn.close()


def reminderSignInfo(r) -> str:
    conn = dbconn.get_db_connection()
    c = conn.cursor()
    # 查询当日群成员 是否签到
    rows = query_by_date(r,'2022-01-01 00:00:00')
    for row in rows:
        #拼接字符串 /n 换行
        print(row['vx_id'] + " " + row['sign'])

    return "111"

if __name__ == '__main__':

    init_group_info('111', '123', '测试')
    #insert('111', '123', '已签到', '2022-01-01')
    #rows = query_by_date('2022-01-01')
    #for row in rows:
        #拼接字符串
        #print(row['vx_id'] + " " + row['sign'])

