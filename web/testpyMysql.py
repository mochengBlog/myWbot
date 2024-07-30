import pymysql

# 连接数据库


# 执行 SQL 语句
cursor.execute("SELECT * FROM bot_message")
results = cursor.fetchall()

# 处理查询结果
for row in results:
    print(row)

# 关闭连接
cursor.close()
conn.close()