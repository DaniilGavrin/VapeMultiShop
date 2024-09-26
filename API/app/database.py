import quopri
from sqlite3 import connect
import sqlite3
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
        

class DatabaseLITE:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()
        self.create_tables_pods()

    def create_tables_pods(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS pods (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                imageUrl TEXT NOT NULL,
                price REAL NOT NULL,
                наличие BOOLEAN NOT NULL
            )
        ''')
        self.connection.commit()

    def insert_product(self, name, imageUrl, price, наличие):
        self.cursor.execute('''
            INSERT INTO products (name, imageUrl, price, наличие)
            VALUES (?, ?, ?, ?)
        ''', (name, imageUrl, price, наличие))
        self.connection.commit()

    def get_pods(self):
        self.cursor.execute('SELECT * FROM pods')
        return self.cursor.fetchall()

    def close(self):
        self.connection.close()

class DatabaseUSER:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()
        self.create_tables_user()

    def create_tables_user(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user (
                uid INTEGER PRIMARY KEY,
                user_id TEXT NOT NULL UNIQUE,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                token TEXT NOT NULL,
                order_id INTEGER NOT NULL,
                cart_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        ''')

        # Таблица корзины
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS cart (
                cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
                uid INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (uid) REFERENCES users(uid)
            )
        ''')

        # Таблица товаров в корзине
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS cart_items (
                cart_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                cart_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                price DECIMAL(10, 2) NOT NULL,
                FOREIGN KEY (cart_id) REFERENCES cart(cart_id)
            )
        ''')

        # Таблица заказов
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                uid INTEGER NOT NULL,
                total_price DECIMAL(10, 2) NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (uid) REFERENCES users(uid)
            )
        ''')

        # Таблица состава заказов
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS order_items (
                order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                price DECIMAL(10, 2) NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(order_id)
            )
        ''')

        self.connection.commit()

    # Добавление товара в корзину
    def add_to_cart(self, uid, product_id, quantity, price):
        # Получаем корзину пользователя или создаем новую
        self.cursor.execute("SELECT cart_id FROM cart WHERE uid = ?", (uid,))
        result = self.cursor.fetchone()

        if result:
            cart_id = result[0]
        else:
            self.cursor.execute("INSERT INTO cart (uid) VALUES (?)", (uid,))
            cart_id = self.cursor.lastrowid

        # Проверяем, есть ли товар уже в корзине
        self.cursor.execute('''
            SELECT quantity FROM cart_items WHERE cart_id = ? AND product_id = ?
        ''', (cart_id, product_id))

        item = self.cursor.fetchone()

        if item:
            # Обновляем количество товара
            new_quantity = item[0] + quantity
            self.cursor.execute('''
                UPDATE cart_items SET quantity = ? WHERE cart_id = ? AND product_id = ?
            ''', (new_quantity, cart_id, product_id))
        else:
            # Добавляем новый товар в корзину
            self.cursor.execute('''
                INSERT INTO cart_items (cart_id, product_id, quantity, price)
                VALUES (?, ?, ?, ?)
            ''', (cart_id, product_id, quantity, price))

        self.connection.commit()

    # Оформление заказа
    def checkout_order(self, uid):
        # Получаем ID корзины
        self.cursor.execute("SELECT cart_id FROM cart WHERE uid = ?", (uid,))
        cart_id = self.cursor.fetchone()

        if not cart_id:
            raise Exception("Корзина пуста")
        cart_id = cart_id[0]

        # Рассчитываем общую стоимость корзины
        self.cursor.execute('''
            SELECT SUM(quantity * price) FROM cart_items WHERE cart_id = ?
        ''', (cart_id,))
        total_price = self.cursor.fetchone()[0]

        if total_price is None:
            raise Exception("Корзина пуста")

        # Создаем новый заказ
        self.cursor.execute('''
            INSERT INTO orders (uid, total_price) VALUES (?, ?)
        ''', (uid, total_price))
        order_id = self.cursor.lastrowid

        # Переносим товары из корзины в состав заказа
        self.cursor.execute('''
            INSERT INTO order_items (order_id, product_id, quantity, price)
            SELECT ?, product_id, quantity, price FROM cart_items WHERE cart_id = ?
        ''', (order_id, cart_id))

        # Очищаем корзину
        self.cursor.execute("DELETE FROM cart_items WHERE cart_id = ?", (cart_id,))
        self.connection.commit()

    # Очистка корзины пользователя
    def clear_cart(self, uid):
        self.cursor.execute("SELECT cart_id FROM cart WHERE uid = ?", (uid,))
        cart_id = self.cursor.fetchone()

        if cart_id:
            self.cursor.execute("DELETE FROM cart_items WHERE cart_id = ?", (cart_id[0],))
            self.connection.commit()

    # Закрытие соединения
    def close(self):
        self.connection.close()
