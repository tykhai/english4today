import sqlite3
import json
from datetime import datetime

DB_NAME = "english_learning.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT, 
        username TEXT UNIQUE, 
        password TEXT, 
        role TEXT, 
        allow_reading_part INTEGER DEFAULT 1, 
        allow_vocab_part INTEGER DEFAULT 1)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS reading_lessons (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        level TEXT, 
        title TEXT, 
        content TEXT, 
        grammar_points TEXT, 
        quiz TEXT)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS vocabulary (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        vocab_date TEXT, 
        word TEXT UNIQUE, 
        word_type TEXT, 
        phonetic TEXT, 
        meaning TEXT, 
        prefix TEXT, 
        suffix TEXT, 
        funny_story TEXT, 
        other_forms TEXT, 
        context_easy TEXT, 
        context_medium TEXT, 
        context_hard TEXT)''')
    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin')")
        conn.commit()
    except sqlite3.IntegrityError: 
        pass
    conn.close()