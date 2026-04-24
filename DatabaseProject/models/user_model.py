from utils.db_connection import get_db_connection

def get_user_by_credentials(email, password):
    conn = get_db_connection()
    user = conn.execute(
        'SELECT * FROM users WHERE email = ? AND password = ?', (email, password)
    ).fetchone()
    conn.close()
    return user

def register_user(name, email, password):
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO users (name, email, password) VALUES (?, ?, ?)', (name, email, password)
    )
    conn.commit()
    conn.close()
