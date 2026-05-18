from utils.db_connection import get_db_connection

def create_order(user_id, total, address, phone, receipt_email, receipt_path=None):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO orders (user_id, total, order_date, address, phone, receipt_email, receipt_path)
        VALUES (?, ?, CURRENT_TIMESTAMP, ?, ?, ?, ?)
    """, (user_id, total, address, phone, receipt_email, receipt_path))

    order_id = cur.lastrowid
    conn.commit()
    conn.close()
    return order_id

def save_receipt_path(order_id, receipt_path):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE orders SET receipt_path = ? WHERE id = ?", (receipt_path, order_id))
    conn.commit()
    conn.close()

def get_order_items(order_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT b.title, oi.quantity, b.price 
        FROM order_items oi
        JOIN books b ON oi.book_id = b.id
        WHERE oi.order_id = ?
    """, (order_id,))
    items = cur.fetchall()
    conn.close()
    return items


def add_order_item(order_id, book_id, quantity, price):
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO order_items (order_id, book_id, quantity, price) VALUES (?, ?, ?, ?)',
        (order_id, book_id, quantity, price)
    )
    conn.commit()
    conn.close()


    