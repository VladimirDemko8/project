import sqlite3 as sl

con = sl.connect('delivery_db.db')

with con:
    con.execute("PRAGMA foreign_keys = ON")
    con.execute(
        """
        CREATE TABLE users (
           user_id INTEGER PRIMARY KEY,
           name TEXT,
           phone TEXT,
           address TEXT
        );
        """
    )
    con.execute("""
        CREATE TABLE products (
           product_id INTEGER PRIMARY KEY,
           name TEXT,
           description TEXT,
           price REAL,
           amount INTEGER,
           rating REAL
        );
        """
    )
    con.execute(
        """
        CREATE TABLE cart (
           user_id INTEGER,
           product_id INTEGER,
           amount INTEGER,
           FOREIGN KEY (user_id) REFERENCES users(user_id),
           FOREIGN KEY (product_id) REFERENCES products(product_id)
        );
        """
    )

    con.execute(
        """
        CREATE TABLE orders (
           order_id INTEGER PRIMARY KEY,
           user_id INTEGER,
           address TEXT,
           delivery_time TEXT,
           payment TEXT,
           status TEXT DEFAULT "ожидание",
           FOREIGN KEY (user_id) REFERENCES users(user_id)
        );
        """
    )

    con.execute(
        """
        CREATE TABLE comments (
           comment_id INTEGER PRIMARY KEY,
           user_id INTEGER,
           product_id INTEGER,
           order_id INTEGER,
           comment TEXT,
           FOREIGN KEY (user_id) REFERENCES users(user_id),
           FOREIGN KEY (product_id) REFERENCES products(product_id),
           FOREIGN KEY (order_id) REFERENCES orders(order_id)
        );

        """
    )
    con.execute(
        """
        CREATE TABLE admins (
           admin_id INTEGER PRIMARY KEY,
           login TEXT,
           password TEXT,

        );    
        """
    ),
    con.execute(
        """
               CREATE TABLE managers (
                  manager_id INTEGER PRIMARY KEY,
                  login TEXT,
                  password TEXT,
               );    
        """
    )
