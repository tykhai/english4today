import streamlit as st

def execute_speech(text_to_speak, label="🔊 Nghe phát âm"):
    # Dọn dẹp ký tự để chuỗi JavaScript không bị gãy
    clean_text = text_to_speak.replace("'", "\\'").replace('"', '\\"').replace("\n", " ").replace("**", "")
    
    # Tạo một nút bấm HTML tự tạo sự kiện đọc trực tiếp trên client (Không re-run app)
    button_html = f"""
    <button onclick="window.speakEnglishText('{clean_text}')" style="
        width: 100%;
        background-color: #4F46E5;
        color: white;
        padding: 10px 16px;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.2);
        transition: all 0.2s;
    " onmouseover="this.style.backgroundColor='#4338CA'" onmouseout="this.style.backgroundColor='#4F46E5'">
        {label}
    </button>
    """
    st.markdown(button_html, unsafe_allow_html=True)
