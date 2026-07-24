#Render Giao diện Tổng Quan Trại Chính
import streamlit as st
from typing import Dict, Any
from .player import PlayerData
from .level_engine import LevelEngine

class GameDashboard:
    """Hiển thị UI tổng quan chỉ số của người chơi trên Streamlit."""

    @staticmethod
    def render(player_data: PlayerData) -> None:
        """Vẽ thanh trạng thái (HP, Energy, Level, Gold) lên màn hình."""
        stats = player_data.get_stats()
        if not stats:
            st.error("Không thể tải dữ liệu nhân vật!")
            return

        level = stats['level']
        xp = stats['xp']
        gold = stats['gold']
        gem = stats['gem']
        energy = stats['energy']
        streak = stats['streak']

        current_level_xp_req = LevelEngine.get_xp_required_for_level(level)
        prev_level_xp_req = LevelEngine.get_xp_required_for_level(level - 1) if level > 1 else 0
        
        # Tính toán thanh tiến trình XP cho Level hiện tại
        xp_into_level = xp - prev_level_xp_req
        xp_needed = current_level_xp_req - prev_level_xp_req
        progress_ratio = min(1.0, max(0.0, xp_into_level / xp_needed))

        # CSS Custom cho Profile
        st.markdown("""
        <style>
            .profile-box { background: linear-gradient(90deg, #1E293B 0%, #0F172A 100%); color: white; padding: 15px 20px; border-radius: 12px; border-left: 5px solid #F59E0B; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }
            .stat-badge { background: rgba(255, 255, 255, 0.1); padding: 5px 15px; border-radius: 20px; font-weight: bold; font-size: 14px; margin-right: 10px; display: inline-block;}
            .xp-text { font-size: 12px; color: #94A3B8; margin-top: -10px; margin-bottom: 10px; text-align: right;}
        </style>
        """, unsafe_allow_html=True)

        # Render Header Profile
        html_content = f"""
        <div class="profile-box">
            <div>
                <h3 style="margin: 0; color: #F8FAFC;">⚔️ Lữ Khách Tinh Anh - Lv.{level}</h3>
                <div style="margin-top: 10px;">
                    <span class="stat-badge">🔥 Chuỗi: {streak} ngày</span>
                    <span class="stat-badge">⚡ {energy}/100</span>
                </div>
            </div>
            <div style="text-align: right;">
                <div class="stat-badge" style="color: #FBBF24; border: 1px solid #F59E0B;">💰 {gold} Vàng</div>
                <div class="stat-badge" style="color: #60A5FA; border: 1px solid #3B82F6;">💎 {gem} Gem</div>
            </div>
        </div>
        """
        st.markdown(html_content, unsafe_allow_html=True)
        
        # XP Progress Bar
        st.progress(progress_ratio)
        st.markdown(f"<div class='xp-text'>XP: {xp_into_level} / {xp_needed} (Tổng: {xp})</div>", unsafe_allow_html=True)