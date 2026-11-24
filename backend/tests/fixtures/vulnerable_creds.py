import sqlite3

# Security vulnerability: Hardcoded credentials (Bandit B105)
API_SECRET_KEY = "SUPER_SECRET_PRODUCTION_KEY_12345"

def get_user_data(username):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    # Security vulnerability: SQL Injection pattern (Bandit B608)
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    return cursor.fetchall()
