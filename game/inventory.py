#Hệ thống Túi Đồ & Vật Phẩm
import sqlite3
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class InventoryEngine:
    """Quản lý vật phẩm thu thập được của người chơi (Gem, Mảnh ghép, Thuốc hồi máu...)."""

    def __init__(self, db_name: str, user_id: int):
        self.db_name = db_name
        self.user_id = user_id

    def add_item(self, item_name: str, quantity: int, item_type: str = "material") -> bool:
        """Thêm vật phẩm vào túi đồ."""
        if quantity <= 0:
            return False

        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT item_id, quantity FROM game_inventory WHERE user_id = ? AND item_name = ?",
                    (self.user_id, item_name)
                )
                row = cursor.fetchone()

                if row:
                    new_quantity = row[1] + quantity
                    cursor.execute(
                        "UPDATE game_inventory SET quantity = ? WHERE item_id = ?",
                        (new_quantity, row[0])
                    )
                else:
                    cursor.execute(
                        "INSERT INTO game_inventory (user_id, item_name, quantity, item_type) VALUES (?, ?, ?, ?)",
                        (self.user_id, item_name, quantity, item_type)
                    )
                conn.commit()
                logger.info(f"Added {quantity}x {item_name} to user {self.user_id}'s inventory.")
                return True
        except sqlite3.Error as e:
            logger.error(f"Error adding item to inventory: {e}")
            return False

    def get_inventory(self) -> List[Dict[str, Any]]:
        """Lấy toàn bộ vật phẩm trong túi."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT item_name, quantity, item_type FROM game_inventory WHERE user_id = ? AND quantity > 0",
                    (self.user_id,)
                )
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error fetching inventory: {e}")
            return []