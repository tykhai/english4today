#Hệ thống Thành Tựu
#Module này kiểm tra và trao thưởng danh hiệu khi người chơi đạt các mốc nhất định (VD: Chuỗi học 7 ngày, Hạ 10 Boss).
import sqlite3
import logging
from typing import List, Dict, Any
from .player import PlayerData
from .reward_engine import RewardEngine

logger = logging.getLogger(__name__)

class AchievementEngine:
    """Quản lý hệ thống thành tựu và danh hiệu của người chơi."""

    def __init__(self, db_name: str, player_data: PlayerData, reward_engine: RewardEngine):
        self.db_name = db_name
        self.player_data = player_data
        self.reward_engine = reward_engine
        self._ensure_achievement_table()

    def _ensure_achievement_table(self) -> None:
        """Khởi tạo bảng lưu trữ thành tựu nếu chưa có."""
        query = """
        CREATE TABLE IF NOT EXISTS game_achievements (
            achieve_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            achievement_code TEXT,
            is_unlocked INTEGER DEFAULT 0,
            unlocked_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );
        """
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error creating achievement table: {e}")

    def unlock_achievement(self, achieve_code: str, title: str, reward_gems: int) -> bool:
        """Mở khóa thành tựu và trao thưởng Gem."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                # Kiểm tra xem đã mở khóa chưa
                cursor.execute(
                    "SELECT is_unlocked FROM game_achievements WHERE user_id = ? AND achievement_code = ?",
                    (self.player_data.user_id, achieve_code)
                )
                row = cursor.fetchone()
                
                if row and row[0] == 1:
                    return False # Đã nhận rồi
                
                # Bắt đầu Transaction trao thưởng
                cursor.execute("BEGIN TRANSACTION;")
                if row is None:
                    cursor.execute(
                        "INSERT INTO game_achievements (user_id, achievement_code, is_unlocked, unlocked_at) VALUES (?, ?, 1, datetime('now'))",
                        (self.player_data.user_id, achieve_code)
                    )
                else:
                    cursor.execute(
                        "UPDATE game_achievements SET is_unlocked = 1, unlocked_at = datetime('now') WHERE user_id = ? AND achievement_code = ?",
                        (self.player_data.user_id, achieve_code)
                    )
                
                # Cộng thưởng
                cursor.execute(
                    "UPDATE game_player SET gem = gem + ? WHERE user_id = ?",
                    (reward_gems, self.player_data.user_id)
                )
                cursor.execute("COMMIT;")
                
                logger.info(f"User {self.player_data.user_id} unlocked achievement: {title}")
                return True
        except sqlite3.Error as e:
            logger.error(f"Error unlocking achievement {achieve_code}: {e}")
            return False

    def get_unlocked_achievements(self) -> List[str]:
        """Lấy danh sách mã thành tựu đã mở khóa."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT achievement_code FROM game_achievements WHERE user_id = ? AND is_unlocked = 1",
                    (self.player_data.user_id,)
                )
                return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error fetching achievements: {e}")
            return []