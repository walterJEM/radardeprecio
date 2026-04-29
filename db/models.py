import sqlite3
from datetime import datetime

DB_PATH = "priceradar.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE,
            name TEXT,
            site TEXT,
            image TEXT,
            created_at TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            price REAL,
            scraped_at TEXT,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)
    conn.commit()
    conn.close()

def save_price(product: dict):
    conn = sqlite3.connect(DB_PATH)
    now = datetime.now().isoformat()

    # Inserta o actualiza el producto
    conn.execute("""
        INSERT INTO products (url, name, site, image, created_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(url) DO UPDATE SET
            name = excluded.name,
            image = excluded.image
    """, (product["url"], product["name"], product["site"], product["image"], now))

    # Obtiene el id del producto
    cur = conn.execute("SELECT id FROM products WHERE url = ?", (product["url"],))
    product_id = cur.fetchone()[0]

    # Guarda el precio en el historial
    conn.execute("""
        INSERT INTO price_history (product_id, price, scraped_at)
        VALUES (?, ?, ?)
    """, (product_id, product["price"], now))

    conn.commit()
    conn.close()

def get_price_history(url: str) -> list:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute("""
        SELECT ph.price, ph.scraped_at
        FROM price_history ph
        JOIN products p ON p.id = ph.product_id
        WHERE p.url = ?
        ORDER BY ph.scraped_at ASC
    """, (url,))
    rows = cur.fetchall()
    conn.close()
    return [{"price": r[0], "scraped_at": r[1]} for r in rows]

def detect_price_drop(url: str) -> dict | None:
    history = get_price_history(url)
    if len(history) < 2:
        return None

    last = history[-1]["price"]
    previous = history[-2]["price"]

    if last < previous:
        drop = previous - last
        pct = round((drop / previous) * 100, 1)
        return {"previous": previous, "current": last, "drop": drop, "pct": pct}
    return None

def get_all_products() -> list:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute("""
        SELECT p.id, p.name, p.site, p.url,
               ph.price as last_price,
               ph.scraped_at as last_scraped
        FROM products p
        LEFT JOIN price_history ph ON ph.product_id = p.id
        WHERE ph.id = (
            SELECT MAX(id) FROM price_history
            WHERE product_id = p.id
        )
    """)
    rows = cur.fetchall()
    conn.close()
    return [
        {
            "id": r[0],
            "name": r[1],
            "site": r[2],
            "url": r[3],
            "last_price": r[4],
            "last_scraped": r[5],
        }
        for r in rows
    ]

def get_price_history_by_id(product_id: int) -> list:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute("""
        SELECT p.name, p.site, p.url,
               ph.price, ph.scraped_at
        FROM price_history ph
        JOIN products p ON p.id = ph.product_id
        WHERE ph.product_id = ?
        ORDER BY ph.scraped_at ASC
    """, (product_id,))
    rows = cur.fetchall()
    conn.close()
    if not rows:
        return []
    return {
        "name": rows[0][0],
        "site": rows[0][1],
        "url": rows[0][2],
        "history": [
            {"price": r[3], "scraped_at": r[4]}
            for r in rows
        ]
    }