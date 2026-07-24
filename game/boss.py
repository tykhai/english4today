#Trận chiến & Hiệu ứng
import streamlit as st
import random
import time
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class BossBattleEngine:
    """Động cơ quản lý trận đánh Boss với hiệu ứng UI/UX Streamlit."""
    
    # Cấu hình âm thanh dưới dạng Base64 hoặc URL (Dùng URL placeholder chuẩn cho production, bạn thay bằng file tĩnh trong thư mục dự án)
    HIT_SOUND_URL = "https://actions.google.com/sounds/v1/impacts/crash.ogg"
    WIN_SOUND_URL = "https://actions.google.com/sounds/v1/cartoon/clank_and_wobble.ogg"

    def __init__(self, db_name: str, user_id: int, day_date: str, boss_level: int = 1):
        self.db_name = db_name
        self.user_id = user_id
        self.day_date = day_date
        self.boss_level = boss_level # 1: Tiểu yêu, 2: Đại tướng, 3: Trùm cuối
        self.multiplier = boss_level
        self._init_battle_state()

    def check_available(self, user_id):
        """Kiểm tra xem user đã khiêu chiến boss trong ngày chưa hoặc đủ điều kiện chưa."""
        # Viết logic kết nối SQLite để kiểm tra trong database ở đây
        # Ví dụ giả lập trả về True (cho phép đánh):
        return True

    def _init_battle_state(self) -> None:
        """Khởi tạo máu và trạng thái vào session state để Streamlit không bị reset."""
        if 'boss_hp' not in st.session_state:
            # Boss HP = 20 từ * hệ số lặp (multiplier)
            st.session_state.boss_max_hp = 20 * self.multiplier
            st.session_state.boss_hp = 20 * self.multiplier
            st.session_state.player_max_hp = 5
            st.session_state.player_hp = 5
            st.session_state.battle_status = "ONGOING" # ONGOING, WIN, LOSE
            st.session_state.trigger_hit_fx = False
            st.session_state.trigger_damage_fx = False

    def render_effects(self) -> None:
        """Render CSS animation và Audio HTML5."""
        css = """
        <style>
        @keyframes shake {
            0% { transform: translate(1px, 1px) rotate(0deg); }
            10% { transform: translate(-1px, -2px) rotate(-1deg); }
            20% { transform: translate(-3px, 0px) rotate(1deg); }
            30% { transform: translate(3px, 2px) rotate(0deg); }
            40% { transform: translate(1px, -1px) rotate(1deg); }
            50% { transform: translate(-1px, 2px) rotate(-1deg); }
            60% { transform: translate(-3px, 1px) rotate(0deg); }
            70% { transform: translate(3px, 1px) rotate(-1deg); }
            80% { transform: translate(-1px, -1px) rotate(1deg); }
            90% { transform: translate(1px, 2px) rotate(0deg); }
            100% { transform: translate(1px, -2px) rotate(-1deg); }
        }
        @keyframes flashRed {
            0% { background-color: rgba(239, 68, 68, 0.2); }
            50% { background-color: rgba(239, 68, 68, 0.8); }
            100% { background-color: transparent; }
        }
        .shake-element { animation: shake 0.5s; }
        .flash-element { animation: flashRed 0.5s; }
        .boss-card { background: #1E293B; padding: 20px; border-radius: 15px; text-align: center; color: white; border: 3px solid #EF4444; }
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)

        if st.session_state.trigger_hit_fx:
            st.markdown(f'<audio autoplay style="display:none;"><source src="{self.HIT_SOUND_URL}" type="audio/mpeg"></audio>', unsafe_allow_html=True)
            st.session_state.trigger_hit_fx = False
            
        if st.session_state.battle_status == "WIN":
             st.markdown(f'<audio autoplay style="display:none;"><source src="{self.WIN_SOUND_URL}" type="audio/mpeg"></audio>', unsafe_allow_html=True)

    def process_answer(self, is_correct: bool) -> None:
        """Xử lý logic trừ máu khi đánh."""
        if is_correct:
            st.session_state.boss_hp -= 1
            st.session_state.trigger_hit_fx = True
            if st.session_state.boss_hp <= 0:
                st.session_state.battle_status = "WIN"
        else:
            st.session_state.player_hp -= 1
            st.session_state.trigger_damage_fx = True
            if st.session_state.player_hp <= 0:
                st.session_state.battle_status = "LOSE"

    def render_ui(self) -> None:
        """Hiển thị UI trận chiến."""
        self.render_effects()
        
        boss_class = "boss-card shake-element" if st.session_state.trigger_hit_fx else "boss-card"
        player_bg = "flash-element" if st.session_state.trigger_damage_fx else ""
        st.session_state.trigger_damage_fx = False # Reset sau khi render frame
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"<div class='{player_bg}' style='padding: 10px; border-radius: 10px;'>", unsafe_allow_html=True)
            st.subheader("🛡️ Player HP")
            st.progress(max(0, st.session_state.player_hp) / st.session_state.player_max_hp)
            st.write(f"Máu: {st.session_state.player_hp} / {st.session_state.player_max_hp}")
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"<div class='{boss_class}'>", unsafe_allow_html=True)
            boss_name = "👹 TIỂU YÊU" if self.boss_level == 1 else "🦹 ĐẠI TƯỚNG" if self.boss_level == 2 else "🐉 TRÙM CUỐI"
            st.markdown(f"<h3>{boss_name}</h3>", unsafe_allow_html=True)
            st.progress(max(0, st.session_state.boss_hp) / st.session_state.boss_max_hp)
            st.write(f"HP: {st.session_state.boss_hp} / {st.session_state.boss_max_hp}")
            st.markdown("</div>", unsafe_allow_html=True)

        if st.session_state.battle_status == "WIN":
            st.success("🎉 CHIẾN THẮNG! Boss đã bị tiêu diệt. Bạn nhận được +500 XP và x3 Gold!")
            if st.button("🏆 Trở về Camp", use_container_width=True):
                # Trigger logic cộng thưởng qua RewardEngine ở đây
                st.session_state.pop('boss_hp', None)
                st.rerun()
                
        elif st.session_state.battle_status == "LOSE":
            st.error("💀 BẠN ĐÃ BỊ HẠ GỤC! Đừng nản lòng, hãy hồi máu và làm lại nhé.")
            if st.button("🔄 Thử thách lại", use_container_width=True):
                st.session_state.pop('boss_hp', None)
                st.rerun()