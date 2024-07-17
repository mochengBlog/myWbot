import datetime
import sqlite3
import db.dbconn as dbconn


def query_by_date(room_id, date):
    conn = dbconn.get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM group_sign ")
    rows = c.fetchall()
    conn.close()
    return rows

if __name__ == '__main__':

    print(query_by_date('123', '2022-01-01 00:00:00'))