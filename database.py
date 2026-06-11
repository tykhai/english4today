import sqlite3

DB_NAME = "english_learning.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. Bảng thành viên
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT, 
        username TEXT UNIQUE, 
        password TEXT, 
        role TEXT, 
        allow_reading_part INTEGER DEFAULT 1, 
        allow_vocab_part INTEGER DEFAULT 1)''')
    
    # 2. Bảng bài đọc
    cursor.execute('''CREATE TABLE IF NOT EXISTS reading_lessons (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        level TEXT, 
        title TEXT, 
        content TEXT, 
        grammar_points TEXT, 
        quiz TEXT)''')
    
    # 3. Bảng từ vựng
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
    
    # Khởi tạo tài khoản Admin mặc định nếu chưa có
    try:
        cursor.execute("""
            INSERT INTO users (username, password, role, allow_reading_part, allow_vocab_part) 
            VALUES ('admin', 'admin123', 'admin', 1, 1)
        """)
        conn.commit()
    except sqlite3.IntegrityError: 
        pass
        
    conn.close()