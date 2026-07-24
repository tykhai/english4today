# game/level_engine.py Hệ thống Cày Cuốc
import logging

logger = logging.getLogger(__name__)

class LevelEngine:
    """Xử lý logic cấp độ (Scaling)."""
    
    @staticmethod
    def get_xp_required_for_level(level: int) -> int:
        """Công thức tính XP cần để lên cấp tiếp theo. VD: Cấp 1 cần 100, Cấp 2 cần 250..."""
        if level < 1:
            return 100
        return int(100 * (1.5 ** (level - 1)))

    @staticmethod
    def calculate_level(total_xp: int) -> int:
        """Tính toán level hiện tại dựa trên tổng XP."""
        level = 1
        while total_xp >= LevelEngine.get_xp_required_for_level(level):
            total_xp -= LevelEngine.get_xp_required_for_level(level)
            level += 1
        return level