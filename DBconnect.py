import mysql.connector
from mysql.connector import Error

class DBConnection:
    def __init__(self):
        self.url = "localhost"
        self.database = "hackerton"
        self.user = "root"
        self.password = "021001"

    def get_connection(self):
        try:
            connection = mysql.connector.connect(
                host=self.url,
                database=self.database,
                user=self.user,
                password=self.password,
                charset='utf8'
            )
            if connection.is_connected():
                print("MySQL database에 성공적으로 연결되었습니다.")
                return connection
        except Error as e:
            print("데이터베이스 연결 오류: ", e)
            return None

    def get_cursor(self):
        connection = self.get_connection()  # 데이터베이스 연결
        if connection:
            return connection.cursor(), connection  # 커서와 연결 객체 반환
        else:
            return None, None
   
    def commit(self, connection):
        if connection:
            connection.commit()

    def rollback(self, connection):
        if connection:
            connection.rollback()

    def close_connection(self, connection):
        if connection and connection.is_connected():
            connection.close()
