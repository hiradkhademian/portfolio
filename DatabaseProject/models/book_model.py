from utils.db_connection import get_db_connection

def get_all_books():
    conn = get_db_connection()
    books = conn.execute('SELECT * FROM books').fetchall()
    conn.close()
    return books

def add_book(title, author, price, stock, image, description, series, category):
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO books (title, author, price, stock, image, description, series, category) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        (title, author, price, stock, image, description, series, category)
    )
    conn.commit()
    conn.close()


def update_book(book_id, title, author, price, stock, image, description, series, category):
    conn = get_db_connection()
    conn.execute(
        'UPDATE books SET title = ?, author = ?, price = ?, stock = ?, image = ?, description = ?, series = ?, category = ? WHERE id = ?',
        (title, author, price, stock, image, description, series, category, book_id)
    )
    conn.commit()
    conn.close()

def delete_book(book_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM books WHERE id = ?', (book_id,))
    conn.commit()
    conn.close()
