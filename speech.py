import streamlit as st
from gtts import gTTS
import io

def execute_speech(text_to_speak):
    """
    Sử dụng gTTS để sinh audio từ backend.
    Giải quyết triệt để lỗi chặn Sandbox trên Mobile và lỗi click lần 2 trên Desktop.
    """
    if not text_to_speak:
        return
    
    try:
        # Làm sạch text sơ bộ
        clean_text = text_to_speak.replace("**", "").replace("*", "")
        
        # Tạo đối tượng chuyển đổi ngôn ngữ (English - US)
        tts = gTTS(text=clean_text, lang='en', tld='com', slow=False)
        
        # Ghi dữ liệu vào bộ nhớ tạm (BytesIO) để không cần lưu file vật lý xuống đĩa cứng
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        
        # Phát audio bằng widget native của Streamlit, tự động phát ngay khi nạp
        st.audio(fp, format="audio/mp3", autoplay=True)
    except Exception as e:
        st.error(f"❌ Lỗi hệ thống phát âm: {e}")