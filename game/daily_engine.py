#Chuỗi Đăng Nhập & Năng Lượng
import sqlite3
import logging
from datetime import datetime, timedelta
from .player import PlayerData

logger = logging.getLogger(__name__)

class DailyEngine:
    """Quản lý điểm danh (Streak) và hồi phục năng lượng hằng ngày."""

    def __init__(self, player_data: PlayerData):
        self.player_data = player_data

    def check_and_update_daily_login(self) -> bool:
        """Kiểm tra lần đăng nhập cuối, cập nhật chuỗi Streak và hồi Energy."""
        try:
            with sqlite3.connect(self.player_data.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT last_login, streak FROM game_player WHERE user_id = ?", (self.player_data.user_id,))
                row = cursor.fetchone()
                
                if not row:
                    return False
                    
                last_login_str, current_streak = row
                today_str = datetime.now().strftime("%Y-%m-%d")
                
                if last_login_str == today_str:
                    return False # Đã đăng nhập hôm nay, không làm gì cả
                    
                last_login_date = datetime.strptime(last_login_str, "%Y-%m-%d").date()
                today_date = datetime.strptime(today_str, "%Y-%m-%d").date()
                
                if today_date - last_login_date == timedelta(days=1):
                    # Đăng nhập liên tục
                    new_streak = current_streak + 1
                else:
                    # Đứt chuỗi
                    new_streak = 1
                    
                # Cập nhật thông tin và hồi 100 Năng lượng mỗi ngày mới
                cursor.execute(
                    "UPDATE game_player SET last_login = ?, streak = ?, energy = 100 WHERE user_id = ?",
                    (today_str, new_streak, self.player_data.user_id)
                )
                conn.commit()
                logger.info(f"User {self.player_data.user_id} daily login updated. Streak: {new_streak}")
                return True
        except sqlite3.Error as e:
            logger.error(f"Error updating daily login: {e}")
            return False