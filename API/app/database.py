import quopri
from sqlite3 import connect
import _mysql_connector

class Database:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.conn = None
        self.cursor = None

    def connect(self):
        self.conn = _mysql_connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )
        self.cursor = self.conn.cursor()
        self.check_table_user(self.cursor)

    def check_table_user(self, cursor):
        # Проверяем существование таблицы через IF NOT EXISTS
        try:
            if self.cursor != None:
                create_table_query = """
                CREATE TABLE IF NOT EXISTS user (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(255) NOT NULL UNIQUE,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB;
                """
                self.cursor.execute(create_table_query)
                # Отправляем изменения
                self.conn.commit()

            else:
                Database.connect()

        except _mysql_connector.Error as e:
            print(f"Ошибка при работе с MySQL: {e}")
        finally:
            cursor.close()

    def validate_auth(self, token, uid):
        try:
            query = "SELECT * FROM user WHERE token=%s AND uid=%s"
            self.cursor.execute(query, (token, uid))
            user = self.cursor.fetchone()
            return user is not None
        except _mysql_connector.Error as e:
            print(f"Ошибка при проверке авторизации: {e}")
            return False

    def get_products(self):
        try:
            query = "SELECT * FROM products"
            self.cursor.execute(query)
            products = self.cursor.fetchall()
            return products
        except _mysql_connector.Error as e:
            print(f"Ошибка при получении продуктов: {e}")
            return(f"Error: {e}")

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("Соединение с MySQL закрыто.")
        