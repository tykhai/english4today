#Hệ thống Phần Thưởng
import logging
import random
from typing import Dict
from .player import PlayerData
from .inventory import InventoryEngine
from .xp_engine import XPEngine

logger = logging.getLogger(__name__)

class RewardEngine:
    """Xử lý việc rớt đồ (Drop rate) và trao thưởng sau các trận đấu/nhiệm vụ."""

    def __init__(self, player_data: PlayerData, inventory_engine: InventoryEngine):
        self.player_data = player_data
        self.inventory_engine = inventory_engine
        self.xp_engine = XPEngine(player_data)

    def grant_room_clear_reward(self) -> Dict[str, int]:
        """Thưởng khi qua 1 phòng (1 từ vựng) trong Dungeon."""
        xp_gain = random.randint(10, 20)
        gold_gain = random.randint(1, 5)
        
        self.xp_engine.add_xp(xp_gain)
        self.player_data.update_stat('gold', gold_gain, is_relative=True)
        
        # 10% cơ hội rớt Mảnh Ghép Khai Sáng (Dùng cho Collection)
        if random.random() <= 0.10:
            self.inventory_engine.add_item("Mảnh Ghép Khai Sáng", 1, "shard")
            return {"xp": xp_gain, "gold": gold_gain, "shard": 1}
            
        return {"xp": xp_gain, "gold": gold_gain, "shard": 0}

    def grant_boss_defeat_reward(self, boss_level: int) -> Dict[str, int]:
        """Thưởng lớn khi hạ Boss cuối ngày."""
        base_xp = 150
        base_gold = 50
        
        total_xp = base_xp * boss_level
        total_gold = base_gold * boss_level
        gems = boss_level * 2
        
        self.xp_engine.add_xp(total_xp)
        self.player_data.update_stat('gold', total_gold, is_relative=True)
        self.player_data.update_stat('gem', gems, is_relative=True)
        
        # Thưởng rương vật phẩm
        self.inventory_engine.add_item("Rương Dũng Giả", 1, "chest")
        
        return {"xp": total_xp, "gold": total_gold, "gem": gems, "chest": 1}