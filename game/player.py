#Quản lý Data Player
import sqlite3
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class PlayerData:
    """Lớp Model xử lý dữ liệu người chơi trong game."""
    
    def __init__(self, db_name: str, user_id: int):
        self.db_name = db_name
        self.user_id = user_id
        self._ensure_player_exists()

    def _ensure_player_exists(self) -> None:
        """Kiểm tra và khởi tạo dữ liệu game cho user nếu chưa có."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT player_id FROM game_player WHERE user_id = ?", (self.user_id,))
                if not cursor.fetchone():
                    cursor.execute(
                        "INSERT INTO game_player (user_id, last_login) VALUES (?, ?)", 
                        (self.user_id, datetime.now().strftime("%Y-%m-%d"))
                    )
                    conn.commit()
                    logger.info(f"Created new game profile for user_id {self.user_id}")
        except sqlite3.Error as e:
            logger.error(f"Error ensuring player exists: {e}")

    def get_stats(self) -> Optional[Dict[str, Any]]:
        """Lấy toàn bộ chỉ số của người chơi."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT xp, level, gold, gem, energy, streak FROM game_player WHERE user_id = ?", 
                    (self.user_id,)
                )
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None
        except sqlite3.Error as e:
            logger.error(f"Error fetching player stats: {e}")
            return None

    def update_stat(self, stat_name: str, value: int, is_relative: bool = True) -> bool:
        """
        Cập nhật 1 chỉ số của người chơi.
        is_relative = True: Cộng/trừ vào số hiện tại (value = 10 -> stat += 10).
        is_relative = False: Set cứng giá trị (value = 10 -> stat = 10).
        """
        valid_stats = ['xp', 'level', 'gold', 'gem', 'energy', 'streak']
        if stat_name not in valid_stats:
            logger.warning(f"Invalid stat name: {stat_name}")
            return False

        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                if is_relative:
                    query = f"UPDATE game_player SET {stat_name} = {stat_name} + ? WHERE user_id = ?"
                else:
                    query = f"UPDATE game_player SET {stat_name} = ? WHERE user_id = ?"
                
                cursor.execute(query, (value, self.user_id))
                conn.commit()
                return True
        except sqlite3.Error as e:
            logger.error(f"Error updating stat {stat_name}: {e}")
            return False