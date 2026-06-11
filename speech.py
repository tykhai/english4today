import streamlit as st

def execute_speech(text_to_speak):
    """Sử dụng cơ chế chèn script trực tiếp vào cửa sổ cha để tránh bị chặn bởi Iframe Sandbox"""
    if not text_to_speak:
        return
        
    clean_text = text_to_speak.replace("'", "\\'").replace('"', '\\"').replace("\n", " ").replace("**", "")
    js_code = f"""
    <script>
        if ('speechSynthesis' in window) {{
            window.speechSynthesis.cancel();
            setTimeout(() => {{
                let msg = new SpeechSynthesisUtterance('{clean_text}');
                msg.lang = 'en-US';
                msg.rate = 0.85;
                msg.volume = 1.0;
                window.speechSynthesis.speak(msg);
            }}, 50);
        }} else {{
            console.error("Trình duyệt không hỗ trợ SpeechSynthesis");
        }}
    </script>
    """
    st.components.v1.html(js_code, height=0, width=0)