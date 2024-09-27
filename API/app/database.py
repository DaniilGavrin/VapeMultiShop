import quopri
from sqlite3 import connect
import sqlite3
import hashlib

SALT = "bB_eygUmMRpIuevFoMGU-mv_FDHhKsdM"

class HashUtil:
    @staticmethod
    def hash_password(password: str) -> str:
        """Хеширует пароль с солью"""
        salted_password = password + SALT
        return hashlib.sha512(salted_password.encode()).hexdigest()
        
class DatabaseLITE:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()

    def insert_product(self, name, imageUrl, price, наличие):
        self.cursor.execute('''
            INSERT INTO products (name, imageUrl, price, наличие)
            VALUES (?, ?, ?, ?)
        ''', (name, imageUrl, price, наличие))
        self.connection.commit()

    def get_products(self):
        self.cursor.execute('SELECT * FROM products')
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
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                imageUrl TEXT NOT NULL,
                price REAL NOT NULL,
                categories TEXT NOT NULL,
                наличие BOOLEAN NOT NULL
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                uid INTEGER PRIMARY KEY,
                user_id TEXT UNIQUE,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                token TEXT NOT NULL,
                order_id TEXT UNIQUE,
                cart_id TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS cart (
                cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
                uid INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (uid) REFERENCES users(uid)
            )
        ''')

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

    def check_valid_login(self, username: str, password: str) -> bool:
        """Проверяет валидность логина и пароля"""
        self.cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
        user = self.cursor.fetchone()

        if not user:
            self.close()
            return False

        # Повторно хешируем полученный хэш пароля с солью и сравниваем с хэшем в базе данных
        hashed_input_password = HashUtil.hash_password(password)
        if user[0] == hashed_input_password:
            self.close()
            return True
        self.close()
        return False

    def add_to_cart(self, uid, product_id, quantity, price):
        self.cursor.execute("SELECT cart_id FROM cart WHERE uid = ?", (uid,))
        result = self.cursor.fetchone()

        if result:
            cart_id = result[0]
        else:
            self.cursor.execute("INSERT INTO cart (uid) VALUES (?)", (uid,))
            cart_id = self.cursor.lastrowid

        self.cursor.execute('''
            SELECT quantity FROM cart_items WHERE cart_id = ? AND product_id = ?
        ''', (cart_id, product_id))

        item = self.cursor.fetchone()

        if item:
            new_quantity = item[0] + quantity
            self.cursor.execute('''
                UPDATE cart_items SET quantity = ? WHERE cart_id = ? AND product_id = ?
            ''', (new_quantity, cart_id, product_id))
        else:
            self.cursor.execute('''
                INSERT INTO cart_items (cart_id, product_id, quantity, price)
                VALUES (?, ?, ?, ?)
            ''', (cart_id, product_id, quantity, price))

        self.connection.commit()

    def checkout_order(self, uid):
        self.cursor.execute("SELECT cart_id FROM cart WHERE uid = ?", (uid,))
        cart_id = self.cursor.fetchone()

        if not cart_id:
            raise Exception("Корзина пуста")
        cart_id = cart_id[0]

        self.cursor.execute('''
            SELECT SUM(quantity * price) FROM cart_items WHERE cart_id = ?
        ''', (cart_id,))
        total_price = self.cursor.fetchone()[0]

        if total_price is None:
            raise Exception("Корзина пуста")

        self.cursor.execute('''
            INSERT INTO orders (uid, total_price) VALUES (?, ?)
        ''', (uid, total_price))
        order_id = self.cursor.lastrowid

        self.cursor.execute('''
            INSERT INTO order_items (order_id, product_id, quantity, price)
            SELECT ?, product_id, quantity, price FROM cart_items WHERE cart_id = ?
        ''', (order_id, cart_id))

        self.cursor.execute("DELETE FROM cart_items WHERE cart_id = ?", (cart_id,))
        self.connection.commit()

    def clear_cart(self, uid):
        self.cursor.execute("SELECT cart_id FROM cart WHERE uid = ?", (uid,))
        cart_id = self.cursor.fetchone()

        if cart_id:
            self.cursor.execute("DELETE FROM cart_items WHERE cart_id = ?", (cart_id[0],))
            self.connection.commit()

    def close(self):
        self.connection.close()