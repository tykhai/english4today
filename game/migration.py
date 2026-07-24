#Khởi tạo Database Game
import sqlite3
import logging
from typing import Optional

# Cấu hình logging cơ bản
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GameDatabaseMigration:
    """Class quản lý việc migration các bảng dữ liệu cho Game Module."""
    
    def __init__(self, db_name: str):
        self.db_name = db_name

    def run_migrations(self) -> bool:
        """Thực thi tạo bảng nếu chưa tồn tại. Dùng Transaction để đảm bảo an toàn."""
        query_player = """
        CREATE TABLE IF NOT EXISTS game_player (
            player_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            gold INTEGER DEFAULT 0,
            gem INTEGER DEFAULT 0,
            energy INTEGER DEFAULT 100,
            streak INTEGER DEFAULT 0,
            last_login TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );
        """
        
        query_inventory = """
        CREATE TABLE IF NOT EXISTS game_inventory (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            item_name TEXT,
            quantity INTEGER DEFAULT 0,
            item_type TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );
        """

        query_dungeon_progress = """
        CREATE TABLE IF NOT EXISTS game_dungeon_progress (
            progress_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            day_date TEXT,
            cleared_rooms INTEGER DEFAULT 0,
            boss_defeated INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );
        """

        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("BEGIN TRANSACTION;")
                cursor.execute(query_player)
                cursor.execute(query_inventory)
                cursor.execute(query_dungeon_progress)
                cursor.execute("COMMIT;")
            logger.info("Game module database migration completed successfully.")
            return True
        except sqlite3.Error as e:
            logger.error(f"Database migration failed: {e}")
            return False