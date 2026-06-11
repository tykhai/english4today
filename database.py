import psycopg2
from psycopg2.extras import DictCursor

# ĐIỀN CHUỖI URI KẾT NỐI SUPABASE CỦA BẠN VÀO ĐÂY
DB_URI = "postgresql://postgres:KhaiHa.2705@db.xgixilajyehjdcauoleh.supabase.co:5432/postgres"

def get_db_connection():
    """Hàm tạo kết nối tới Supabase PostgreSQL"""
    conn = psycopg2.connect(DB_URI, cursor_factory=DictCursor)
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Bảng thành viên (PostgreSQL dùng SERIAL thay vì AUTOINCREMENT)
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id SERIAL PRIMARY KEY, 
        username TEXT UNIQUE, 
        password TEXT, 
        role TEXT, 
        allow_reading_part INTEGER DEFAULT 1, 
        allow_vocab_part INTEGER DEFAULT 1)''')
    
    # 2. Bảng bài đọc
    cursor.execute('''CREATE TABLE IF NOT EXISTS reading_lessons (
        id SERIAL PRIMARY KEY, 
        level TEXT, 
        title TEXT, 
        content TEXT, 
        grammar_points TEXT, 
        quiz TEXT)''')
    
    # 3. Bảng từ vựng
    cursor.execute('''CREATE TABLE IF NOT EXISTS vocabulary (
        id SERIAL PRIMARY KEY, 
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
            ON CONFLICT (username) DO NOTHING
        """)
        conn.commit()
    except Exception as e:
        print(f"Lỗi khởi tạo Admin: {e}")
        
    cursor.close()
    conn.close()