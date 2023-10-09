SELECT_USER_QUERY = "SELECT name FROM users WHERE telegram_id = ?"

INSERT_USER_QUERY = """
INSERT INTO users (name, phone, address, telegram_id) 
VALUES (?, ?, ?, ?)
"""


SELECT_ADMINS_QUERY = "SELECT * FROM admins WHERE login = ? AND password = ?"
SELECT_MANAGERS_QUERY = "SELECT * FROM managers WHERE login = ? AND password = ?"

UPDATE_USER_PHONE_QUERY = "UPDATE users SET phone = ? WHERE user_id = ?"
UPDATE_USER_ADDRESS_QUERY = "UPDATE users SET address = ? WHERE user_id = ?"


SHOW_CART_QUERY = """
            SELECT p.product_id, p.name, p.price, c.amount
            FROM cart c
            JOIN products p ON p.product_id = c.product
            WHERE c.cart_id = ?"""

