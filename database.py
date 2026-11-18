import sqlite3
import csv
import os
from contextlib import contextmanager

class ProductDatabase:
    def __init__(self, db_path="products.db"):
        self.db_path = db_path
        self.init_db()

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    price REAL NOT NULL,
                    availability TEXT NOT NULL,
                    product_url TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def insert_product(self, title, price, availability, product_url):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO products (title, price, availability, product_url)
                    VALUES (?, ?, ?, ?)
                """, (title.strip(), float(price), availability.strip(), product_url.strip()))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None

    def insert_many(self, product_records):
        inserted_count = 0
        skipped_count = 0
        for item in product_records:
            result = self.insert_product(
                title=item["title"],
                price=item["price"],
                availability=item["availability"],
                product_url=item["product_url"]
            )
            if result is not None:
                inserted_count += 1
            else:
                skipped_count += 1
        return inserted_count, skipped_count

    def get_all_products(self, limit=None, offset=0):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if limit is not None:
                cursor.execute("""
                    SELECT id, title, price, availability, product_url, created_at
                    FROM products
                    ORDER BY id ASC
                    LIMIT ? OFFSET ?
                """, (int(limit), int(offset)))
            else:
                cursor.execute("""
                    SELECT id, title, price, availability, product_url, created_at
                    FROM products
                    ORDER BY id ASC
                """)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_product_by_id(self, product_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, title, price, availability, product_url, created_at
                FROM products
                WHERE id = ?
            """, (product_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def search_products(self, query=None, min_price=None, max_price=None):
        sql = "SELECT id, title, price, availability, product_url, created_at FROM products WHERE 1=1"
        params = []

        if query:
            sql += " AND LOWER(title) LIKE ?"
            params.append(f"%{query.lower().strip()}%")

        if min_price is not None:
            sql += " AND price >= ?"
            params.append(float(min_price))

        if max_price is not None:
            sql += " AND price <= ?"
            params.append(float(max_price))

        sql += " ORDER BY price ASC"

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, tuple(params))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_price_extremes(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, title, price, availability, product_url, created_at
                FROM products
                ORDER BY price ASC
                LIMIT 1
            """)
            cheapest = cursor.fetchone()

            cursor.execute("""
                SELECT id, title, price, availability, product_url, created_at
                FROM products
                ORDER BY price DESC
                LIMIT 1
            """)
            expensive = cursor.fetchone()

            return (
                dict(cheapest) if cheapest else None,
                dict(expensive) if expensive else None
            )

    def get_average_price(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT ROUND(AVG(price), 2) FROM products")
            result = cursor.fetchone()[0]
            return float(result) if result is not None else 0.0

    def get_total_count(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM products")
            return cursor.fetchone()[0]

    def update_product(self, product_id, title=None, price=None, availability=None):
        fields = []
        params = []

        if title is not None:
            fields.append("title = ?")
            params.append(title.strip())

        if price is not None:
            fields.append("price = ?")
            params.append(float(price))

        if availability is not None:
            fields.append("availability = ?")
            params.append(availability.strip())

        if not fields:
            return False

        params.append(product_id)
        sql = f"UPDATE products SET {', '.join(fields)} WHERE id = ?"

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, tuple(params))
            conn.commit()
            return cursor.rowcount > 0

    def delete_product(self, product_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
            conn.commit()
            return cursor.rowcount > 0

    def export_to_csv(self, file_path="products_export.csv"):
        products = self.get_all_products()
        if not products:
            return 0

        directory = os.path.dirname(file_path)
        if directory:
            os.makedirs(directory, exist_ok=True)

        fieldnames = ["id", "title", "price", "availability", "product_url", "created_at"]
        with open(file_path, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(products)

        return len(products)
