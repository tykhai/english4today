# game/xp_engine.py Hệ thống Cày Cuốc
import logging
from typing import Tuple
from .player import PlayerData
from .level_engine import LevelEngine

logger = logging.getLogger(__name__)

class XPEngine:
    """Quản lý việc nhận XP và Level Up."""
    
    def __init__(self, player_data: PlayerData):
        self.player_data = player_data

    def add_xp(self, amount: int) -> Tuple[bool, bool, int]:
        """
        Cộng XP cho người chơi. 
        Returns: (Thành công?, Có lên cấp không?, Cấp mới là bao nhiêu)
        """
        if amount <= 0: return False, False, 0
        
        stats = self.player_data.get_stats()
        if not stats: return False, False, 0
        
        old_level = stats['level']
        new_xp = stats['xp'] + amount
        new_level = LevelEngine.calculate_level(new_xp)
        
        # Cập nhật DB trong 1 transaction
        success = self.player_data.update_stat('xp', amount, is_relative=True)
        if not success: return False, False, 0
        
        is_leveled_up = new_level > old_level
        if is_leveled_up:
            self.player_data.update_stat('level', new_level, is_relative=False)
            # Thưởng khi lên cấp: Full năng lượng, tặng 10 Gold
            self.player_data.update_stat('energy', 100, is_relative=False)
            self.player_data.update_stat('gold', 10 * (new_level - old_level), is_relative=True)
            logger.info(f"User {self.player_data.user_id} leveled up to {new_level}!")
            
        return True, is_leveled_up, new_level