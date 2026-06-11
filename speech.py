import streamlit as st
import time  

def execute_speech(text_to_speak):
    # Bỏ các dấu nháy đơn và dọn dẹp ký tự xuống dòng để tránh lỗi chuỗi JavaScript
    clean_text = text_to_speak.replace("'", "\\'").replace("\n", " ").replace("**", "")
    
    # Tạo một chuỗi thời gian ngẫu nhiên để đánh lừa trình duyệt luôn nạp lại iframe
    timestamp = int(time.time() * 1000)
    
    js_code = f"""
    <iframe srcdoc="
        <script>
            // Hủy các giọng đọc cũ đang chạy ẩn để tránh bị đè tiếng
            window.speechSynthesis.cancel();
            
            let u = new SpeechSynthesisUtterance('{clean_text}');
            u.lang = 'en-US'; 
            u.rate = 0.85;
            
            window.speechSynthesis.speak(u);
        </script>
    " style="display:none; width:0; height:0; border:none;" data-time="{timestamp}"></iframe>
    """
    st.html(js_code)
