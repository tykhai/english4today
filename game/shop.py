#Trung Tâm Thương Mại / Cửa Hàng
import streamlit as st
import logging
from typing import Dict, Any
from .player import PlayerData
from .inventory import InventoryEngine

logger = logging.getLogger(__name__)

class ShopEngine:
    """Xử lý giao dịch tại Cửa hàng (Mua vật phẩm bằng Gold/Gem)."""

    # Danh mục vật phẩm trong Cửa hàng
    CATALOG = {
        "item_hp_potion": {
            "name": "Bình Máu Nhỏ 🧪",
            "desc": "Dùng để hồi +2 HP trong trận chiến với Boss.",
            "price_gold": 50,
            "price_gem": 0,
            "type": "consumable",
            "db_name": "HP Potion"
        },
        "item_energy_drink": {
            "name": "Nước Tăng Lực ☕",
            "desc": "Hồi ngay lập tức 50 Thể lực (Energy).",
            "price_gold": 100,
            "price_gem": 0,
            "type": "consumable",
            "db_name": "Energy Drink"
        },
        "item_mystery_shard": {
            "name": "Mảnh Ghép Khai Sáng 🧩",
            "desc": "Mảnh ghép thần bí dùng để mở khóa các truyền thuyết.",
            "price_gold": 0,
            "price_gem": 10,
            "type": "shard",
            "db_name": "Mảnh Ghép Khai Sáng"
        }
    }

    def __init__(self, player_data: PlayerData, inventory_engine: InventoryEngine):
        self.player_data = player_data
        self.inventory = inventory_engine

    def buy_item(self, item_key: str) -> bool:
        """Xử lý logic trừ tiền và thêm vật phẩm."""
        if item_key not in self.CATALOG:
            return False

        item = self.CATALOG[item_key]
        stats = self.player_data.get_stats()
        if not stats: return False

        current_gold = stats['gold']
        current_gem = stats['gem']

        # Kiểm tra đủ tiền không
        if current_gold < item["price_gold"] or current_gem < item["price_gem"]:
            st.error("❌ Bạn không có đủ tài nguyên để mua vật phẩm này!")
            return False

        # Trừ tiền (Sử dụng is_relative=True với giá trị âm)
        if item["price_gold"] > 0:
            self.player_data.update_stat('gold', -item["price_gold"], is_relative=True)
        if item["price_gem"] > 0:
            self.player_data.update_stat('gem', -item["price_gem"], is_relative=True)

        # Thêm vật phẩm vào túi
        self.inventory.add_item(item["db_name"], 1, item["type"])
        st.success(f"🎉 Giao dịch thành công! Nhận được: {item['name']}")
        return True

    def render_shop_ui(self) -> None:
        """Hiển thị giao diện Cửa Hàng trên Streamlit."""
        stats = self.player_data.get_stats()
        if not stats: return
        
        st.markdown("### 🏪 Thương Gia Lang Thang")
        st.write(f"Số dư hiện tại: **💰 {stats['gold']} Vàng** | **💎 {stats['gem']} Gem**")
        st.markdown("---")

        cols = st.columns(3)
        col_idx = 0

        for key, item in self.CATALOG.items():
            with cols[col_idx % 3]:
                with st.container(border=True):
                    st.markdown(f"#### {item['name']}")
                    st.write(f"*{item['desc']}*")
                    
                    price_display = f"💰 {item['price_gold']} Vàng" if item['price_gold'] > 0 else f"💎 {item['price_gem']} Gem"
                    st.markdown(f"**Giá:** {price_display}")
                    
                    # Nút mua hàng (Dùng key riêng để Streamlit không bị nhầm lẫn)
                    if st.button("Mua Ngay", key=f"buy_{key}", use_container_width=True):
                        if self.buy_item(key):
                            st.rerun() # Tải lại trang để cập nhật số dư
                            
            col_idx += 1