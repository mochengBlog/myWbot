import datetime

import pymysql
from pymysql.err import MySQLError
from queue import Queue, Empty
from threading import Thread, Lock
from configuration import Config
from mc.duo_lin_guo import check_duolingo_status


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class DBConnectionPool(metaclass=SingletonMeta):
    def __init__(self, config, max_connections=10):
        if hasattr(DBConnectionPool, '_instance'):
            # 如果实例已经创建，则直接返回实例
            return
        self.config = config
        self.pool = Queue(max_connections)
        self.max_connections = max_connections
        self.lock = Lock()
        self.create_connections()
        # 标记实例已创建
        DBConnectionPool._instance = self

    def create_connections(self):
        while self.pool.qsize() < self.max_connections:
            try:
                connection = pymysql.connect(**self.config)
                self.pool.put(connection)
            except MySQLError as e:
                print(f"Error creating connection: {e}")

    def get_connection(self):
        try:
            return self.pool.get(block=False)
        except Empty:
            print("No available connections in the pool.")
            return None

    def release_connection(self, connection):
        self.pool.put(connection)

    def close_all(self):
        with self.lock:
            while not self.pool.empty():
                connection = self.pool.get()
                connection.close()


class DBUtils(metaclass=SingletonMeta):  # 注意这里应用了元类
    def __init__(self, db_pool):
        self.db_pool = db_pool  # 确保这一行存在
        if hasattr(DBUtils, '_instance'):
            # 如果实例已经创建，则直接返回实例
            return
        self.db_pool = db_pool
        # 标记实例已创建
        DBUtils._instance = self

    def execute_query(self, query, params=None):
        connection = self.get_db_connection()
        if connection is None:
            raise Exception("No available database connections.")
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, params or ())
                result = cursor.fetchall()
            connection.commit()
            return result or []  # 确保返回空列表而不是 None
        except MySQLError as e:
            print(f"Database error: {e}")
            connection.rollback()
            return []  # 在发生错误时返回空列表
        finally:
            self.db_pool.release_connection(connection)

    def insert(self, table, data):
        keys = ', '.join(data.keys())
        values = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO {table} ({keys}) VALUES ({values})"
        self.execute_query(query, list(data.values()))

    def get(self, table, condition=None):
        condition_str = f" WHERE {condition}" if condition else ""
        query = f"SELECT * FROM {table}{condition_str}"
        return self.execute_query(query)

    def update(self, table, data, condition):
        set_clause = ', '.join([f"{k} = %s" for k in data.keys()])
        condition_str = f" WHERE {condition}" if condition else ""
        query = f"UPDATE {table} SET {set_clause}{condition_str}"
        self.execute_query(query, list(data.values()))

    def delete(self, table, condition):
        condition_str = f" WHERE {condition}"
        query = f"DELETE FROM {table}{condition_str}"
        self.execute_query(query)

    def insert_by_robot(self, table: str, data: dict):
        db = DBUtils(db_pool)
        db.insert(table, data)

    def getMessageInfoByCount(self, room_id: str, count: int):
        db = DBUtils(self.db_pool)
        return db.execute_query(
            f"SELECT sender_id,(SELECT NAME FROM room_info WHERE wxid=sender_id AND room_id='{room_id}') AS name,message FROM messages WHERE room_id='{room_id}' AND message_type=1 ORDER BY date  LIMIT {count} ")

    def get_db_connection(self):
        return self.db_pool.get_connection()

    def SignInsert(self, room_id, vx_id, sign):
        # 获取今天日期
        if datetime.datetime.now().hour < 2:
            date = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        else:
            date = datetime.datetime.now().strftime("%Y-%m-%d")

        # 查询是否已经存在
        rows = self.execute_query("SELECT * FROM group_sign WHERE room_id = %s AND vxid = %s AND sign_date = %s",
                                  (room_id, vx_id, date))
        # 查询name 先查是否存在多邻国昵称 否则插入群昵称
        name = ''
        result = self.execute_query("SELECT * FROM duo_lin_guo_user WHERE vxid = %s", (vx_id,))
        if len(result) == 0:
            room_result = self.execute_query("SELECT * FROM room_info WHERE vxid = %s and room_id = %s", (vx_id,room_id))
            name = room_result[0]['name']
        else:
            name = result[0]['name']

        if len(rows) == 0:
            print("插入签到")
            self.execute_query("INSERT INTO group_sign (room_id, vxid, sign, sign_date, name) VALUES (%s, %s, %s, %s)",
                               (room_id, vx_id, sign, date, name))
        else:
            print("更新签到")
            # 如果需要更新，可以在这里添加更新逻辑
            self.execute_query("UPDATE group_sign SET sign = %s WHERE room_id = %s AND vxid = %s AND sign_date = %s",
                               (sign, room_id, vx_id, date, name))
    def DuoLinGuoSignInsert(self, status_dict, room_id):
        # 获取今天日期
        if datetime.datetime.now().hour < 2:
            date = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        else:
            date = datetime.datetime.now().strftime("%Y-%m-%d")

        for user_name, info in status_dict.items():
            status = info['status']
            print(f"用户名: {user_name}, 打卡状态: {status}")

            # 查询vxid

            vxid_result = self.execute_query("SELECT * FROM duo_lin_guo_user WHERE name = %s", (user_name,))
            vxid = vxid_result[0]['vxid']
            name = vxid_result[0]['name']
            # 查询是否已经存在
            rows = self.execute_query("SELECT * FROM group_sign WHERE room_id = %s AND vxid = %s AND sign_date = %s",
                                      (room_id, vxid, date))
            sign = 1 if status == '已打卡' else 0
            if len(rows) == 0:
                print("插入签到")
                self.execute_query("INSERT INTO group_sign (room_id, vxid, sign, sign_date,name,info) VALUES (%s, %s, %s, %s, %s, %s)",
                                   (room_id, vxid, sign, date, name,'多邻国录入打卡'))
            else:
                print("更新签到")
                # 如果需要更新，可以在这里添加更新逻辑
                self.execute_query("UPDATE group_sign SET sign = %s WHERE room_id = %s AND vxid = %s AND sign_date = %s",
                                   (sign, room_id, vxid, date))
    def getDuoLinGuoUser(self):
        # 查询多邻国用户
        rows = self.execute_query("SELECT * FROM duo_lin_guo_user ")
        # 创建用户映射
        user_map = {}

        # 遍历查询结果并填充 user_map
        for row in rows:
            name = row['name']  # 假设每行是字典，并包含 'name' 和 'user_id' 键
            user_id = row['user_id']
            user_map[name] = user_id

        return user_map
    def SignInsertBQ(self, room_id, vx_id, sign, context):
        if "昨天" in context:
            date = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        elif "前天" in context:
            date = (datetime.datetime.now() - datetime.timedelta(days=2)).strftime("%Y-%m-%d")
        else:
            date = datetime.datetime.now().strftime("%Y-%m-%d")  # 默认今天

        # 查询是否已经存在
        rows = self.execute_query("SELECT * FROM group_sign WHERE room_id = %s AND vxid = %s AND sign_date = %s",
                                  (room_id, vx_id, date))
        if len(rows) == 0:
            print("插入签到")
            self.execute_query("INSERT INTO group_sign (room_id, vxid, sign, sign_date,info) VALUES (%s, %s, %s, %s,'补签')",
                               (room_id, vx_id, sign, date))
        else:
            print("更新签到")
            # 如果需要更新，可以在这里添加更新逻辑
            self.execute_query("UPDATE group_sign SET sign = %s , info = '补签' WHERE room_id = %s AND vxid = %s AND sign_date = %s ",
                               (sign, room_id, vx_id, date))


# Usage
if __name__ == "__main__":
    config = Config()
    # 初始化

    # Database configuration
    db_config = {
        'host': config.MySql.get('host'),
        'user': config.MySql.get('user'),
        'password': config.MySql.get('password'),
        'db': config.MySql.get('database'),
        'charset': 'utf8mb4',
        'cursorclass': pymysql.cursors.DictCursor
    }

    # Create a connection pool
    # 确保只创建一次连接池
    db_pool = DBConnectionPool(db_config, max_connections=5)

    # 确保只创建一次DBUtils实例
    db_utils = DBUtils(db_pool)
    # 根据条件 查询聊天记录  1 时间倒序查询100条 2 根据时间日期查询
    # rows = db_utils.getMessageInfoByCount("24236590105@chatroom", 100)

    # messages = []
    # if not rows:
    #     print("No rows found.")
    # else:
    #     for row in rows:
    #         sender_id = row['sender_id']
    #         sender_name = row['name']
    #         message = row['message']
    #         messages.append(f"{sender_name}说:{message}")
    # print(messages)
    # db_utils.SignInsertBQ('111', '123', 1, "前天");
    user_map = db_utils.getDuoLinGuoUser()

    print(user_map)
    status_dict = check_duolingo_status(user_map)
    # 将所有用户的打卡状态合并到一个字符串中
    db_utils.DuoLinGuoSignInsert(status_dict,"43541810338@chatroom")


    # print('\n'.join(status_lines))

