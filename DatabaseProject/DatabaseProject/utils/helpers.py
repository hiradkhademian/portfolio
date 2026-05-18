from flask import session

def is_admin():
    return session.get('username') == 'Admin'

def is_logged_in():
    return 'user_id' in session
