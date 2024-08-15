import datetime

import pymysql
from pymysql.err import MySQLError
from queue import Queue, Empty
from threading import Thread, Lock
from configuration import Config


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
        connection = self.db_pool.get_connection()
        if connection is None:
            raise Exception("No available database connections.")
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, params or ())
                result = cursor.fetchall()
            connection.commit()
            return result
        except MySQLError as e:
            print(f"Database error: {e}")
            connection.rollback()
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

    def insert_by_robot(self, table: str, data : dict):
        db = DBUtils(db_pool)
        db.insert(table, data)
    def getMessageInfoByCount(self,room_id: str, count: int):
        db = DBUtils(self.db_pool)
        return db.execute_query(f"SELECT sender_id,(SELECT NAME FROM room_info WHERE wxid=sender_id AND room_id='{room_id}') AS name,message FROM messages WHERE room_id='{room_id}' AND message_type=1 ORDER BY date  LIMIT {count} ")





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
    rows = db_utils.getMessageInfoByCount("24236590105@chatroom", 100)

    messages = []
    if not rows:
        print("No rows found.")
    else:
        for row in rows:
            sender_id = row['sender_id']
            sender_name = row['name']
            message = row['message']
            messages.append(f"{sender_name}说:{message}")
    print(messages)
