#Hầm Ngục 20 Phòng Học
import sqlite3
import logging
import streamlit as st
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class DungeonEngine:
    """Quản lý tiến trình leo tháp (20 phòng) tương ứng với 20 từ vựng mỗi ngày."""

    MAX_ROOMS = 20

    def __init__(self, db_name: str, user_id: int, day_date: str):
        self.db_name = db_name
        self.user_id = user_id
        self.day_date = day_date
        self._ensure_dungeon_progress()

    def _ensure_dungeon_progress(self) -> None:
        """Tạo bản ghi tiến trình hầm ngục cho ngày cụ thể nếu chưa có."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT progress_id FROM game_dungeon_progress WHERE user_id = ? AND day_date = ?",
                    (self.user_id, self.day_date)
                )
                if not cursor.fetchone():
                    cursor.execute(
                        "INSERT INTO game_dungeon_progress (user_id, day_date, cleared_rooms, boss_defeated) VALUES (?, ?, 0, 0)",
                        (self.user_id, self.day_date)
                    )
                    conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error ensuring dungeon progress: {e}")

    def get_progress(self) -> Dict[str, int]:
        """Lấy số phòng đã qua và trạng thái Boss."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT cleared_rooms, boss_defeated FROM game_dungeon_progress WHERE user_id = ? AND day_date = ?",
                    (self.user_id, self.day_date)
                )
                row = cursor.fetchone()
                return {"cleared_rooms": row[0], "boss_defeated": row[1]} if row else {"cleared_rooms": 0, "boss_defeated": 0}
        except sqlite3.Error as e:
            logger.error(f"Error fetching dungeon progress: {e}")
            return {"cleared_rooms": 0, "boss_defeated": 0}

    def clear_current_room(self) -> bool:
        """Hoàn thành 1 phòng (học xong 1 từ/quiz)."""
        progress = self.get_progress()
        if progress["cleared_rooms"] >= self.MAX_ROOMS:
            return False # Đã qua hết phòng

        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE game_dungeon_progress SET cleared_rooms = cleared_rooms + 1 WHERE user_id = ? AND day_date = ?",
                    (self.user_id, self.day_date)
                )
                conn.commit()
                return True
        except sqlite3.Error as e:
            logger.error(f"Error clearing room: {e}")
            return False

    def mark_boss_defeated(self) -> bool:
        """Lưu trạng thái đã hạ Boss của ngày."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE game_dungeon_progress SET boss_defeated = 1 WHERE user_id = ? AND day_date = ?",
                    (self.user_id, self.day_date)
                )
                conn.commit()
                return True
        except sqlite3.Error as e:
            logger.error(f"Error defeating boss: {e}")
            return False

    def render_dungeon_map(self) -> None:
        """Hiển thị UI bản đồ 20 phòng."""
        progress = self.get_progress()
        cleared = progress["cleared_rooms"]
        
        st.markdown("### 🏰 Hầm Ngục Từ Vựng (20 Tầng)")
        st.progress(cleared / self.MAX_ROOMS)
        
        cols = st.columns(10)
        for i in range(self.MAX_ROOMS):
            col_idx = i % 10
            room_num = i + 1
            with cols[col_idx]:
                if room_num <= cleared:
                    st.markdown(f"<div style='text-align:center; padding:10px; background:#10B981; color:white; border-radius:5px; margin-bottom:10px;'>✔️<br>T{room_num}</div>", unsafe_allow_html=True)
                elif room_num == cleared + 1:
                    st.markdown(f"<div style='text-align:center; padding:10px; background:#F59E0B; color:white; border-radius:5px; margin-bottom:10px; border: 2px dashed #B45309;'>⚔️<br>T{room_num}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='text-align:center; padding:10px; background:#334155; color:#94A3B8; border-radius:5px; margin-bottom:10px;'>🔒<br>T{room_num}</div>", unsafe_allow_html=True)