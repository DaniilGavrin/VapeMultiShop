import mysql.connector

class database:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def get_connection(self):
        if not self.connection or self.connection.is_connected() == False:
            try:
                self.connection = mysql.connector.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.database
                )
                print("Подключение к базе данных MySQL установлено успешно.")
            except mysql.connector.Error as error:
                print(f"Ошибка подключения к базе данных MySQL: {error}")
        return self.connection

    def close_connection(self):
        if self.connection and self.connection.is_connected():
            try:
                self.connection.close()
                print("Соединение с базой данных MySQL закрыто.")
            except mysql.connector.Error as error:
                print(f"Ошибка при закрытии соединения: {error}")
