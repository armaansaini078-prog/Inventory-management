"""SQLite database layer for the Inventory Management System."""
from pathlib import Path
import sqlite3

DB_PATH = Path(__file__).resolve().with_name("inventory.db")


def connect():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


def init_db():
    with connect() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT '',
                price REAL NOT NULL CHECK(price >= 0),
                quantity INTEGER NOT NULL DEFAULT 0 CHECK(quantity >= 0),
                supplier TEXT NOT NULL DEFAULT '',
                low_stock_level INTEGER NOT NULL DEFAULT 5 CHECK(low_stock_level >= 0),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        con.execute("""
            CREATE TABLE IF NOT EXISTS stock_movements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                movement_type TEXT NOT NULL CHECK(movement_type IN ('IN', 'OUT')),
                quantity INTEGER NOT NULL CHECK(quantity > 0),
                note TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE
            )
        """)


def add_product(name, category, price, quantity, supplier, low_stock_level):
    with connect() as con:
        cur = con.execute(
            "INSERT INTO products(name, category, price, quantity, supplier, low_stock_level) VALUES (?, ?, ?, ?, ?, ?)",
            (name, category, price, quantity, supplier, low_stock_level),
        )
        if quantity > 0:
            con.execute(
                "INSERT INTO stock_movements(product_id, movement_type, quantity, note) VALUES (?, 'IN', ?, 'Opening stock')",
                (cur.lastrowid, quantity),
            )
        return cur.lastrowid


def update_product(product_id, name, category, price, quantity, supplier, low_stock_level):
    with connect() as con:
        old = con.execute("SELECT quantity FROM products WHERE id = ?", (product_id,)).fetchone()
        if old is None:
            raise ValueError("Product nahi mila.")
        difference = quantity - old["quantity"]
        con.execute(
            "UPDATE products SET name=?, category=?, price=?, quantity=?, supplier=?, low_stock_level=? WHERE id=?",
            (name, category, price, quantity, supplier, low_stock_level, product_id),
        )
        if difference:
            con.execute(
                "INSERT INTO stock_movements(product_id, movement_type, quantity, note) VALUES (?, ?, ?, 'Quantity changed from product form')",
                (product_id, "IN" if difference > 0 else "OUT", abs(difference)),
            )


def delete_product(product_id):
    with connect() as con:
        con.execute("DELETE FROM products WHERE id = ?", (product_id,))


def list_products(search="", low_only=False):
    sql = "SELECT * FROM products WHERE (name LIKE ? OR category LIKE ? OR supplier LIKE ? OR CAST(id AS TEXT) LIKE ?)"
    term = f"%{search.strip()}%"
    params = [term, term, term, term]
    if low_only:
        sql += " AND quantity <= low_stock_level"
    sql += " ORDER BY name COLLATE NOCASE"
    with connect() as con:
        return con.execute(sql, params).fetchall()


def get_product(product_id):
    with connect() as con:
        return con.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()


def move_stock(product_id, movement_type, quantity, note=""):
    if movement_type not in ("IN", "OUT"):
        raise ValueError("Movement type galat hai.")
    if quantity <= 0:
        raise ValueError("Quantity 0 se zyada honi chahiye.")
    with connect() as con:
        product = con.execute("SELECT quantity FROM products WHERE id = ?", (product_id,)).fetchone()
        if product is None:
            raise ValueError("Product nahi mila.")
        new_quantity = product["quantity"] + quantity if movement_type == "IN" else product["quantity"] - quantity
        if new_quantity < 0:
            raise ValueError("Stock mein itni quantity available nahi hai.")
        con.execute("UPDATE products SET quantity = ? WHERE id = ?", (new_quantity, product_id))
        con.execute(
            "INSERT INTO stock_movements(product_id, movement_type, quantity, note) VALUES (?, ?, ?, ?)",
            (product_id, movement_type, quantity, note.strip()),
        )


def dashboard_stats():
    with connect() as con:
        row = con.execute("""
            SELECT COUNT(*) AS product_count,
                   COALESCE(SUM(quantity), 0) AS total_units,
                   COALESCE(SUM(price * quantity), 0) AS inventory_value,
                   COALESCE(SUM(CASE WHEN quantity <= low_stock_level THEN 1 ELSE 0 END), 0) AS low_stock_count
            FROM products
        """).fetchone()
        return dict(row)


def movement_history(limit=100):
    with connect() as con:
        return con.execute("""
            SELECT m.id, p.name AS product_name, m.movement_type, m.quantity, m.note, m.created_at
            FROM stock_movements m JOIN products p ON p.id = m.product_id
            ORDER BY m.id DESC LIMIT ?
        """, (limit,)).fetchall()
