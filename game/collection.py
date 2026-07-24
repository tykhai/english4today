#Vương Quốc Từ Vựng - Thu thập Mảnh ghép
import sqlite3
import logging
from typing import List, Dict, Any
from .inventory import InventoryEngine

logger = logging.getLogger(__name__)

class CollectionEngine:
    """Hệ thống ghép thẻ/tranh sử dụng 'Mảnh Ghép Khai Sáng'."""

    # Cấu hình các bộ sưu tập (Lore của Vương quốc)
    COLLECTIONS = {
        "C01": {"title": "Khởi Nguyên Từ Vựng", "cost": 5, "lore": "Ngày xửa ngày xưa, tại thung lũng của những âm tiết..."},
        "C02": {"title": "Bí Ẩn Ngữ Pháp", "cost": 10, "lore": "Những quy tắc được khắc trên đá ngàn năm..."},
        "C03": {"title": "Kỷ Nguyên Đọc Hiểu", "cost": 15, "lore": "Khi con người thấu hiểu được cổ ngữ..."}
    }

    def __init__(self, db_name: str, user_id: int, inventory_engine: InventoryEngine):
        self.db_name = db_name
        self.user_id = user_id
        self.inventory = inventory_engine
        self._ensure_collection_table()

    def _ensure_collection_table(self) -> None:
        """Tạo bảng lưu trữ tiến trình Collection."""
        query = """
        CREATE TABLE IF NOT EXISTS game_collections (
            col_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            collection_code TEXT,
            is_unlocked INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );
        """
        try:
            with sqlite3.connect(self.db_name) as conn:
                conn.execute(query)
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error creating collections table: {e}")

    def unlock_collection(self, collection_code: str) -> bool:
        """Dùng mảnh ghép để mở khóa Lore."""
        if collection_code not in self.COLLECTIONS:
            return False

        cost = self.COLLECTIONS[collection_code]["cost"]
        
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                # Kiểm tra số lượng Mảnh Ghép
                cursor.execute(
                    "SELECT quantity FROM game_inventory WHERE user_id = ? AND item_name = 'Mảnh Ghép Khai Sáng'",
                    (self.user_id,)
                )
                row = cursor.fetchone()
                current_shards = row[0] if row else 0

                if current_shards < cost:
                    return False # Không đủ mảnh ghép

                # Kiểm tra xem đã mở chưa
                cursor.execute(
                    "SELECT is_unlocked FROM game_collections WHERE user_id = ? AND collection_code = ?",
                    (self.user_id, collection_code)
                )
                unlocked_row = cursor.fetchone()
                if unlocked_row and unlocked_row[0] == 1:
                    return False # Đã mở rồi

                # Thực thi Transaction: Trừ mảnh ghép và Mở khóa
                cursor.execute("BEGIN TRANSACTION;")
                cursor.execute(
                    "UPDATE game_inventory SET quantity = quantity - ? WHERE user_id = ? AND item_name = 'Mảnh Ghép Khai Sáng'",
                    (cost, self.user_id)
                )
                
                if unlocked_row is None:
                    cursor.execute(
                        "INSERT INTO game_collections (user_id, collection_code, is_unlocked) VALUES (?, ?, 1)",
                        (self.user_id, collection_code)
                    )
                else:
                    cursor.execute(
                        "UPDATE game_collections SET is_unlocked = 1 WHERE user_id = ? AND collection_code = ?",
                        (self.user_id, collection_code)
                    )
                cursor.execute("COMMIT;")
                logger.info(f"User {self.user_id} unlocked collection {collection_code}")
                return True
        except sqlite3.Error as e:
            logger.error(f"Error unlocking collection {collection_code}: {e}")
            return False

    def get_unlocked_collections(self) -> List[str]:
        """Lấy danh sách mã collection đã mở."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT collection_code FROM game_collections WHERE user_id = ? AND is_unlocked = 1",
                    (self.user_id,)
                )
                return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error fetching collections: {e}")
            return []