import sqlite3
from database import get_connection

def verify_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT username, role, allow_reading_part, allow_vocab_part 
        FROM users WHERE LOWER(username)=LOWER(?) AND password=?
    """, (username.strip(), password.strip()))
    res = cursor.fetchone()
    conn.close()
    if res:
        return {"username": res[0], "role": res[1], "allow_reading": res[2], "allow_vocab": res[3]}
    return None

def add_new_user(username, password, r_p, v_p):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (username, password, role, allow_reading_part, allow_vocab_part) 
            VALUES (?, ?, 'user', ?, ?)
        """, (username.strip(), password.strip(), int(r_p), int(v_p)))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def get_all_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, username, password, role, allow_reading_part, allow_vocab_part FROM users WHERE role != 'admin'")
    users = cursor.fetchall()
    conn.close()
    return users

def update_user_permissions(user_id, allow_reading, allow_vocab):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users SET allow_reading_part=?, allow_vocab_part=? WHERE user_id=?
    """, (int(allow_reading), int(allow_vocab), user_id))
    conn.commit()
    conn.close()

def delete_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()