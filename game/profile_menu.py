#Màn Hình Thành Tựu & Bộ Sưu Tập
import streamlit as st
import sqlite3
from typing import Dict, Any
from .player import PlayerData
from .inventory import InventoryEngine
from .collection import CollectionEngine

class ProfileMenu:
    """Hiển thị giao diện Thành tựu và Bộ sưu tập truyền thuyết của người chơi."""

    @staticmethod
    def render(db_name: str, user_id: int) -> None:
        st.markdown("### 🏆 Sảnh Danh Vang & Truyền Thuyết")
        
        # Lấy thông tin số lượng mảnh ghép hiện tại
        inventory = InventoryEngine(db_name, user_id)
        items = inventory.get_inventory()
        shards_count = 0
        for it in items:
            if it['item_name'] == "Mảnh Ghép Khai Sáng":
                shards_count = it['quantity']

        st.info(f"🧩 Bạn đang sở hữu: **{shards_count} Mảnh Ghép Khai Sáng** trong túi đồ.")
        st.markdown("---")

        # Chia tab hiển thị
        tab1, tab2 = st.tabs(["🏅 Thành Tựu Đạt Được", "📜 Vương Quốc Truyền Thuyết"])

        # TAB 1: THÀNH TỰU
        with tab1:
            st.markdown("#### Danh Hiệu & Mốc Phát Triển")
            
            # Danh sách thành tựu mẫu hệ thống
            achievements_list = [
                {"code": "FIRST_BLOOD", "title": "⚔️ Bước Chân Đầu Tiên", "desc": "Vượt qua phòng Hầm Ngục đầu tiên.", "reward": 5},
                {"code": "STREAK_7", "title": "🔥 Kiên Trì Bền Bỉ", "desc": "Duy trì đăng nhập và học tập 7 ngày liên tiếp.", "reward": 20},
                {"code": "BOSS_SLAYER", "title": "👑 Kẻ Sát Boss", "desc": "Hành quyết thành công Boss cuối ngày.", "reward": 50}
            ]
            
            unlocked_codes = []
            try:
                with sqlite3.connect(db_name) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT achievement_code FROM game_achievements WHERE user_id = ? AND is_unlocked = 1", (user_id,))
                    unlocked_codes = [row[0] for row in cursor.fetchall()]
            except sqlite3.Error:
                pass

            for ach in achievements_list:
                is_unlocked = ach["code"] in unlocked_codes
                status_text = "✅ Đã Mở Khóa" if is_unlocked else "🔒 Chưa Đạt"
                border_color = "#10B981" if is_unlocked else "#334155"
                bg_color = "rgba(16, 185, 129, 0.05)" if is_unlocked else "rgba(255, 255, 255, 0.02)"
                
                st.markdown(f"""
                <div style="border: 2px solid {border_color}; padding: 12px 15px; border-radius: 8px; margin-bottom: 12px; background: {bg_color};">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <strong style="font-size: 16px; color: #F8FAFC;">{ach['title']}</strong>
                        <span style="font-size: 13px; font-weight: bold; color: {'#10B981' if is_unlocked else '#94A3B8'};">{status_text}</span>
                    </div>
                    <p style="color: #94A3B8; font-size: 14px; margin: 5px 0 8px 0;">{ach['desc']}</p>
                    <span style="color: #FBBF24; font-size: 12px;">🎁 Phần thưởng mở khóa: {ach['reward']} Gem</span>
                </div>
                """, unsafe_allow_html=True)

        # TAB 2: BỘ SƯU TẬP (LORE)
        with tab2:
            st.markdown("#### 📜 Các Chương Cổ Ngữ & Truyền Thuyết")
            collections = CollectionEngine.COLLECTIONS
            
            unlocked_cols = []
            try:
                with sqlite3.connect(db_name) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT collection_code FROM game_collections WHERE user_id = ? AND is_unlocked = 1", (user_id,))
                    unlocked_cols = [row[0] for row in cursor.fetchall()]
            except sqlite3.Error:
                pass

            for code, info in collections.items():
                is_open = code in unlocked_cols
                if is_open:
                    st.success(f"📖 **{info['title']}** (Đã mở khóa)\n\n> *\"{info['lore']}\"*")
                else:
                    with st.container(border=True):
                        st.warning(f"🔒 **{info['title']}** (Khóa - Cần {info['cost']} Mảnh Ghép)")
                        st.write(f"Mô tả ẩn: *{info['lore'][:30]}...*")
                        if st.button(f"Mở Khóa Bằng {info['cost']} Mảnh", key=f"unlock_col_{code}"):
                            col_eng = CollectionEngine(db_name, user_id, inventory)
                            if col_eng.unlock_collection(code):
                                st.success(f"🎉 Mở khóa thành công chương: {info['title']}!")
                                st.rerun()
                            else:
                                st.error("❌ Không đủ Mảnh Ghép Khai Sáng hoặc đã mở rồi!")