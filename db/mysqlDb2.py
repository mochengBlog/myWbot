import pymysql

class MySQLUtil:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(MySQLUtil, cls).__new__(cls)
            cls._instance.initialize(*args, **kwargs)
        return cls._instance

    def initialize(self, host, user, password, database, pool_name='mysql_pool', pool_size=5):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.pool_name = pool_name
        self.pool_size = pool_size
        self.pool = None
        self.init_pool()

    def init_pool(self):
        self.pool = connection_from_url(
            f'mysql://{self.user}:{self.password}@{self.host}/{self.database}',
            maxsize=self.pool_size,
            block=True,
            timeout=30
        )

    def get_connection(self):
        return self.pool.get_connection()

    def execute_query(self, query, params=None):
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                result = cursor.fetchall()
        return result

    def insert(self, table, data):
        columns = ', '.join(data.keys())
        values = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({values})"
        self.execute_query(query, tuple(data.values()))

    def update(self, table, data, condition):
        set_clause = ', '.join([f"{key}=%s" for key in data])
        query = f"UPDATE {table} SET {set_clause} WHERE {condition}"
        self.execute_query(query, tuple(data.values()))

    def delete(self, table, condition):
        query = f"DELETE FROM {table} WHERE {condition}"
        self.execute_query(query)

    def select(self, table, columns='*', condition=None):
        query = f"SELECT {', '.join(columns)} FROM {table}"
        if condition:
            query += f" WHERE {condition}"
        return self.execute_query(query)