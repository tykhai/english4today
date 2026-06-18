import streamlit as st
import sqlite3
import json
import re
from datetime import datetime
from streamlit_mic_recorder import mic_recorder

# --- IMPORT TỪ CÁC LỚP ĐÃ TÁCH ---
from database import init_db, DB_NAME
from speech import execute_speech

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="English4Today - Học Gây Nghiện", page_icon="⚡", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .main-header { font-size:34px !important; font-weight: 800; color: #1E3A8A; text-align: center; margin-bottom: 25px; }
    .flashcard { background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%); padding: 30px; border-radius: 20px; border-left: 8px solid #4F46E5; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05); margin-bottom: 20px; }
    /* Giữ nguyên màu chữ sáng tối tự động cho flashcard nếu chạy darkmode */
    [data-theme="dark"] .flashcard { background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%); border-left-color: #6366F1; }
    .story-card { background-color: #FFFBEB; padding: 18px; border-radius: 12px; border: 1px dashed #F59E0B; font-style: italic; color: #1E293B; }
    .progress-text { font-size: 18px; font-weight: bold; color: #4F46E5; text-align: center; margin-bottom: 10px; }
    .score-box { padding: 25px; border-radius: 20px; text-align: center; margin-top: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border: 2px solid #E2E8F0; }
    .q-result { padding: 8px 12px; border-radius: 6px; margin-top: 8px; font-weight: bold; font-size: 14px; display: inline-block; }
    .voice-status { padding: 12px; border-radius: 10px; background-color: #EFF6FF; border: 1px solid #BFDBFE; margin-top: 10px; }
    
    /* CẤU HÌNH LIÊN QUAN ĐẾN LIGHT/DARK MODE CHO BÀI ĐỌC */
    .reading-box {
        background-color: #F0FDF4; 
        padding: 20px; 
        border-radius: 12px; 
        font-size: 18px; 
        line-height: 1.7; 
        border-left: 4px solid #10B981; 
        margin-bottom: 15px;
        color: #1E293B; /* Mặc định chế độ sáng */
    }
    /* Tự động đảo màu chữ và nền khi người dùng đổi qua giao diện tối (Dark Mode) */
    @media (prefers-color-scheme: dark) {
        .reading-box { background-color: #064E3B; color: #F8FAFC; border-left-color: #34D399; }
    }
    html[data-theme="dark"] .reading-box {
        background-color: #064E3B; 
        color: #F8FAFC; 
        border-left-color: #34D399;
    }
</style>
""", unsafe_allow_html=True)

init_db()

# --- HÀM BỔ TRỢ ---
def clean_and_bold_keyword(sentence, keyword):
    if not sentence: return ""
    return re.sub(re.escape(keyword), f"**{keyword}**", sentence.replace("**", "").replace("*", ""), flags=re.IGNORECASE)

def clean_and_underline_keywords(sentence, keywords_list):
    if not sentence: return ""
    clean_text = sentence.replace("**", "").replace("*", "")
    if not keywords_list:
        return clean_text
    sorted_keywords = sorted(list(set(keywords_list)), key=len, reverse=True)
    for kw in sorted_keywords:
        if kw and kw.strip():
            # Sử dụng raw string bằng r'\b' để tránh SyntaxWarning
            pattern = re.compile(r'\b' + re.escape(kw.strip()) + r'\b', re.IGNORECASE)
            # Khắc phục triệt để lỗi \g bằng chuỗi định dạng raw fr
            clean_text = pattern.sub(fr"<u>\g<0></u>", clean_text)
    return clean_text

def hide_keyword_for_exercise(sentence, keyword):
    if not sentence: return ""
    return re.sub(re.escape(keyword), "_______", sentence.replace("**", "").replace("*", ""), flags=re.IGNORECASE)

def render_result(is_correct, correct_msg):
    if is_correct:
        st.markdown("<div class='q-result' style='background-color: #DCFCE7; color: #14532D;'>🟢 CHÍNH XÁC!</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='q-result' style='background-color: #FEE2E2; color: #7F1D1D;'>❌ CHƯA ĐÚNG -> {correct_msg}</div>", unsafe_allow_html=True)

# --- KHỞI TẠO SESSION STATE ---
states = {
    "user": None, "vocab_index": 0, "current_date": "",
    "reading_submitted": False, "vocab_submitted": False, 
    "vocab_rev_submitted": False, "fill_blank_submitted": False,
    "text_input_en_submitted": False, "text_input_vi_submitted": False,
    "trigger_balloons": False, "trigger_snow": False
}
for key, value in states.items():
    if key not in st.session_state: 
        st.session_state[key] = value

if st.session_state.trigger_balloons:
    st.balloons(); st.session_state.trigger_balloons = False
if st.session_state.trigger_snow:
    st.snow(); st.session_state.trigger_snow = False

# --- MÀN HÌNH ĐĂNG NHẬP ---
if st.session_state.user is None:
    st.markdown("<div class='main-header'>🚀 English4Today - Hệ Thống Học Ngữ Liệu Gây Nghiện</div>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1, 1.3, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("Tài khoản:")
            password = st.text_input("Mật khẩu:", type="password")
            if st.form_submit_button("🔥 Tiến Vào Đấu Trường Học Tập", use_container_width=True):
                conn = sqlite3.connect(DB_NAME)
                res = conn.execute("SELECT username, role, allow_reading_part, allow_vocab_part FROM users WHERE LOWER(username)=LOWER(?) AND password=?", (username.strip(), password.strip())).fetchone()
                conn.close()
                if res:
                    st.session_state.user = {"username": res[0], "role": res[1], "allow_reading": int(res[2]), "allow_vocab": int(res[3])}
                    st.rerun()
                else: 
                    st.error("❌ Sai tài khoản hoặc mật khẩu!")
    st.stop()

user = st.session_state.user

# --- SIDEBAR NAV ---
with st.sidebar:
    st.markdown(f"### 🎉 Chiến binh: **{user['username']}**\n---")
    menu = []
    if user['allow_reading'] == 1 or user['role'] == 'admin': menu.append("📚 Thử Thách Bài Đọc")
    if user['allow_vocab'] == 1 or user['role'] == 'admin': menu.append("🧠 Từ Vựng Theo Ngày")
    if user['role'] == 'admin': menu.append("⚙️ Trung Tâm Admin")
    
    if not menu:
        st.warning("Tài khoản chưa được phân quyền.")
        choice = None
    else:
        choice = st.radio("Lộ trình hằng ngày:", menu)
        
    st.markdown("---")
    if st.button("Đăng xuất 🚪", use_container_width=True):
        st.session_state.user = None
        st.rerun()

# --- PHẦN 1: THỬ THÁCH BÀI ĐỌC ---
if choice == "📚 Thử Thách Bài Đọc":
    st.markdown("<div class='main-header'>📚 Luyện Ngữ Liệu & Thử Thách Đọc Hiểu</div>", unsafe_allow_html=True)
    conn = sqlite3.connect(DB_NAME)
    lessons = conn.execute("SELECT id, level, title, content, grammar_points, quiz FROM reading_lessons").fetchall()
    all_vocab_words = [r[0] for r in conn.execute("SELECT word FROM vocabulary").fetchall()]
    conn.close()

    if not lessons: 
        st.info("Chưa có bài đọc nào.")
    else:
        levels = sorted(list(set([r[1] for r in lessons])))
        selected_lvl = st.segmented_control("Chọn cấp độ trình độ:", levels, default=levels[0])
        filtered = [l for l in lessons if l[1] == selected_lvl]
        
        if filtered:
            sel_title = st.selectbox("Chọn bài viết mục tiêu:", [l[2] for l in filtered])
            l_id, lvl, title, content, grammar_points, quiz_json = [l for l in filtered if l[2] == sel_title][0]
            
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                col1.markdown(f"### 📖 {title}")
                with col2:
                    if st.button("🔊 Đọc Toàn Bộ Bài Văn", use_container_width=True, key=f"read_btn_{l_id}"):
                        execute_speech(content)
                
                underlined_content = clean_and_underline_keywords(content, all_vocab_words)
                st.markdown(f"<div class='reading-box'>{underlined_content}</div>", unsafe_allow_html=True)
                
                with st.expander("💡 Xem Cấu Trúc Ngữ Pháp Chuyên Sâu"):
                    if grammar_points:
                        try:
                            for g in json.loads(grammar_points):
                                st.warning(f"🔷 Cấu trúc: {g.get('structures')}")
                                st.write(f"👉 Giải thích: {g.get('explanation')}")
                        except: st.write(grammar_points)
                
                st.markdown("### 🎯 Đấu Trường Đọc Hiểu")
                if quiz_json:
                    try:
                        quizzes = json.loads(quiz_json)
                        user_answers = []
                        for idx, q in enumerate(quizzes):
                            with st.container(border=True):
                                st.markdown(f"**Question {idx+1}: {q['question']}**")
                                ans = st.radio("Chọn câu trả lời:", q['options'], key=f"r_q_{l_id}_{idx}", disabled=st.session_state.reading_submitted)
                                user_answers.append(ans)
                                if st.session_state.reading_submitted:
                                    render_result(ans == q['answer'], f"Đáp án: {q['answer']}")
                        
                        st.markdown("---")
                        if not st.session_state.reading_submitted:
                            if st.button("🚀 Nộp Bài & Chấm Điểm Bài Đọc", use_container_width=True):
                                score_test = sum(1 for idx, q in enumerate(quizzes) if user_answers[idx] == q['answer'])
                                ratio = score_test / len(quizzes)
                                if score_test == len(quizzes): st.session_state.trigger_balloons = True
                                elif ratio >= 0.8: st.session_state.trigger_snow = True
                                st.session_state.reading_submitted = True
                                st.rerun()
                        else:
                            score = sum(1 for idx, q in enumerate(quizzes) if user_answers[idx] == q['answer'])
                            total_q = len(quizzes)
                            ratio = score / total_q
                            bg_color, border_color, text_color, comment = ("#ECFDF5", "#10B981", "#064E3B", "🔥 Tuyệt đỉnh thiên tài!") if score == total_q else (("#EFF6FF", "#3B82F6", "#1E3A8A", "🌟 Xuất sắc!") if ratio >= 0.8 else ("#F8FAFC", "#94A3B8", "#1E293B", "👍 Khá tốt! Hãy nghiên cứu kỹ lại nhé!"))
                            st.markdown(f"<div class='score-box' style='background: {bg_color}; border: 2px solid {border_color}; color: {text_color};'><h3>🏆 KẾT QUẢ TỔNG KẾT ĐẤU TRƯỜNG</h3><p style='font-size: 28px; font-weight: 800; margin: 10px 0;'>Bạn đạt: {score} / {total_q} Câu đúng</p><p style='font-size: 16px; font-weight: 600;'>💡 Lời khuyên: {comment}</p></div>", unsafe_allow_html=True)
                            if st.button("🔄 Làm Lại Bài Đọc Này", use_container_width=True):
                                st.session_state.reading_submitted = False
                                st.rerun()
                    except: st.write("Lỗi cấu trúc câu hỏi.")

# --- PHẦN 2: TỪ VỰNG THEO NGÀY ---
elif choice == "🧠 Từ Vựng Theo Ngày":
    st.markdown("<div class='main-header'>🧠 Sổ Tay Từ Vựng Thông Minh Theo Ngày</div>", unsafe_allow_html=True)
    conn = sqlite3.connect(DB_NAME)
    dates = [r[0] for r in conn.execute("SELECT DISTINCT TRIM(vocab_date) FROM vocabulary ORDER BY vocab_date DESC").fetchall()]
    conn.close()

    if not dates: 
        st.info("Chưa có từ vựng nào.")
    else:
        selected_date = st.selectbox("📆 Chọn ngày học tập mục tiêu:", dates)
        if st.session_state.current_date != selected_date:
            st.session_state.vocab_index = 0
            st.session_state.current_date = selected_date
            st.session_state.vocab_submitted = False
            st.session_state.vocab_rev_submitted = False
            st.session_state.fill_blank_submitted = False
            st.session_state.text_input_en_submitted = False
            st.session_state.text_input_vi_submitted = False
            
        conn = sqlite3.connect(DB_NAME)
        vocabs = conn.execute("SELECT word, word_type, phonetic, meaning, prefix, suffix, funny_story, other_forms, context_easy, context_medium, context_hard FROM vocabulary WHERE TRIM(vocab_date)=?", (selected_date,)).fetchall()
        conn.close()
        
        total_words = len(vocabs)
        if total_words > 0:
            tab_learn, tab_game, tab_game_rev, tab_input_en, tab_input_vi, tab_fill = st.tabs([
                "🌟 Thẻ Flashcard", 
                "⚔️ Trắc Nghiệm (A -> V)", 
                "🔄 Trắc Nghiệm (V -> A)", 
                "⌨️ Gõ Từ (V -> A)",
                "📝 Gõ Nghĩa (A -> V)",
                "✏️ Chỗ Trống"
            ])
            
            # TAB 1: FLASHCARD LEARNING
            with tab_learn:
                idx = st.session_state.vocab_index
                st.markdown(f"<div class='progress-text'>⚡ TIẾN ĐỘ: Từ {idx+1} / {total_words}</div>", unsafe_allow_html=True)
                st.progress((idx + 1) / total_words)
                word, w_type, phonetic, meaning, prefix, suffix, story, other_forms, c_easy, c_medium, c_hard = vocabs[idx]
                
                st.markdown(f"<div class='flashcard'><span style='font-size:36px; font-weight:bold; color:#4F46E5;'>{word}</span> <span style='background-color:#EEF2F6; color:#64748B; font-size:14px; padding:4px 8px; border-radius:6px;'>{w_type.upper()}</span><p style='font-size: 18px; margin-top:10px;'>🗣️ Phiên âm: <code>{phonetic}</code> | <strong>Ý nghĩa: {meaning}</strong></p></div>", unsafe_allow_html=True)
                
                col_audio1, col_audio2 = st.columns(2)
                with col_audio1:
                    if st.button("🔊 Nghe Phát Âm Mẫu", key=f"spk_{word}", use_container_width=True):
                        execute_speech(word)
                        
                with col_audio2:
                    st.write("🎙️ **Đấu Trường Luyện Nói & Chấm Điểm AI:**")
                    
                    # Sử dụng Thẻ r"" (raw string) để bọc toàn bộ Regex bên trong JavaScript, loại bỏ triệt để SyntaxWarning dòng 351
                    js_speech_ai = fr"""
                    <div style="margin-bottom: 10px;">
                        <button id="start-rec-btn" style="width: 100%; padding: 10px; background-color: #EF4444; color: white; border: none; border-radius: 8px; font-weight: bold; cursor: pointer;">
                            🔴 Bấm Để Nói & Chấm Điểm
                        </button>
                    </div>
                    <div id="rec-status" style="padding: 10px; border-radius: 6px; background-color: #F3F4F6; color: #374151; font-size: 14px; font-weight: 500; border: 1px solid #E5E7EB;">
                        Trạng thái: Sẵn sàng thực hiện thử thách.
                    </div>

                    <script>
                        const btn = document.getElementById('start-rec-btn');
                        const statusDiv = document.getElementById('rec-status');
                        const targetWord = "{word.lower().strip()}";

                        btn.onclick = function() {{
                            if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {{
                                statusDiv.innerHTML = "❌ Lỗi: Trình duyệt của bạn không hỗ trợ nhận diện giọng nói (SpeechRecognition). Khuyến nghị dùng Google Chrome.";
                                statusDiv.style.backgroundColor = "#FEE2E2";
                                statusDiv.style.color = "#991B1B";
                                return;
                            }}

                            navigator.mediaDevices.getUserMedia({{ audio: true }})
                            .then(function(stream) {{
                                const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                                const recognition = new SpeechRecognition();
                                recognition.lang = 'en-US';
                                recognition.interimResults = false;
                                recognition.maxAlternatives = 1;

                                recognition.onstart = function() {{
                                    btn.innerHTML = "⏳ Hệ thống đang nghe bạn nói...";
                                    btn.style.backgroundColor = "#F59E0B";
                                    statusDiv.innerHTML = "🎙️ Đang ghi âm... Hãy đọc to từ: <b>" + targetWord + "</b>";
                                    statusDiv.style.backgroundColor = "#EFF6FF";
                                    statusDiv.style.color = "#1E40AF";
                                }};

                                recognition.onerror = function(event) {{
                                    btn.innerHTML = "🔴 Bấm Để Nói & Chấm Điểm";
                                    btn.style.backgroundColor = "#EF4444";
                                    if(event.error === 'not-allowed') {{
                                        statusDiv.innerHTML = "❌ Lỗi: Quyền truy cập Microphone bị từ chối! Hãy cấp quyền cho trình duyệt.";
                                    }} else {{
                                        statusDiv.innerHTML = "❌ Không nhận dạng được âm thanh (Lỗi: " + event.error + "). Hãy thử lại.";
                                    }}
                                    statusDiv.style.backgroundColor = "#FEE2E2";
                                    statusDiv.style.color = "#991B1B";
                                }};

                                recognition.onend = function() {{
                                    btn.innerHTML = "🔴 Bấm Để Nói & Chấm Điểm";
                                    btn.style.backgroundColor = "#EF4444";
                                }};

                                recognition.onresult = function(event) {{
                                    const resultText = event.results[0][0].transcript.toLowerCase().trim();
                                    const confidence = event.results[0][0].confidence;
                                    
                                    const cleanResult = resultText.replace(/[.,\/#!\?\$%\^&\*;:{{}}=\-_`~()]/g,"");
                                    
                                    if(cleanResult === targetWord) {{
                                        let score = Math.round(confidence * 100);
                                        if (score < 70) score = 85; 
                                        statusDiv.innerHTML = "🟢 <b>CHÍNH XÁC!</b> Đọc được: '" + resultText + "' -> Điểm phát âm: <b>" + score + "/100</b>";
                                        statusDiv.style.backgroundColor = "#DCFCE7";
                                        statusDiv.style.color = "#166534";
                                    }} else {{
                                        statusDiv.innerHTML = "❌ <b>CHƯA KHỚP!</b> Bạn đọc là: '" + resultText + "' (Từ đích: " + targetWord + "). Hãy cố gắng phát âm rõ chữ hơn nhé!";
                                        statusDiv.style.backgroundColor = "#FEE2E2";
                                        statusDiv.style.color = "#991B1B";
                                    }}
                                }};

                                recognition.start();
                                stream.getTracks().forEach(track => track.stop());
                            }})
                            .catch(function(err) {{
                                statusDiv.innerHTML = "❌ Lỗi phần cứng: Không tìm thấy thiết bị Microphone kết nối hoặc quyền truy cập bị chặn! (" + err.name + ")";
                                statusDiv.style.backgroundColor = "#FEE2E2";
                                statusDiv.style.color = "#991B1B";
                            }});
                        }};
                    </script>
                    """
                    # Đã thay thế st.components.v1.html bằng st.iframe theo chuẩn mới nhất của Streamlit năm 2026
                    st.iframe(f"data:text/html;charset=utf-8,{js_speech_ai}", height=140)

                st.markdown("---")
                col_l, col_r = st.columns([1, 1])
                with col_l:
                    st.markdown(f"<div class='story-card'><strong>💡 Mẹo kể chuyện liên tưởng:</strong><br><br>{story}</div>", unsafe_allow_html=True)
                    mm_text = f"🌟 Từ Khóa: {word} ({w_type})\n├── 🧬 Tiền tố: {prefix or 'N/A'}\n├── 🧬 Hậu tố: {suffix or 'N/A'}\n└── 🌿 Gia đình từ:\n" + "".join([f"    {line}\n" for line in (other_forms or "").split('\n')])
                    st.code(mm_text, language="text")
                with col_r:
                    st.markdown("#### 🧬 Các Loại Từ Liên Quan")
                    st.info(other_forms or "Chưa bổ sung.")
                    st.markdown("#### 🎯 Ngữ Cảnh Ứng Dụng")
                    st.write("🟢 **Dễ:**", clean_and_bold_keyword(c_easy, word))
                    st.write("🔵 **Vừa:**", clean_and_bold_keyword(c_medium, word))
                    st.write("🔴 **Khó:**", clean_and_bold_keyword(c_hard, word))

                st.markdown("---")
                col_prev, _, col_next = st.columns([1, 2, 1])
                if col_prev.button("⬅️ Từ Trước Đó", use_container_width=True, disabled=(idx == 0)):
                    st.session_state.vocab_index -= 1; st.rerun()
                if col_next.button("Từ Tiếp Theo ➡️", use_container_width=True, disabled=(idx == total_words - 1)):
                    st.session_state.vocab_index += 1; st.rerun()

            # TAB 2: GAME XUÔI (ANH -> VIỆT)
            with tab_game:
                st.markdown("### ⚔️ Thử Thách Chọn Nghĩa Tiếng Việt Đúng")
                game_answers = []
                for idx, v_item in enumerate(vocabs):
                    g_word, g_correct_meaning = v_item[0], v_item[3]
                    options = sorted(list(set([g_correct_meaning] + list(set([v[3] for v in vocabs if v[3] != g_correct_meaning]))[:3])))
                    with st.container(border=True):
                        st.markdown(f"🎯 Từ số {idx+1}: **{g_word}** nghĩa là gì?")
                        u_ans = st.radio(f"Chọn đáp án:", options, key=f"gm_v_{g_word}", disabled=st.session_state.vocab_submitted)
                        game_answers.append((u_ans, g_correct_meaning))
                        if st.session_state.vocab_submitted:
                            render_result(u_ans == g_correct_meaning, f"Nghĩa chuẩn xác là: {g_correct_meaning}")
                
                st.markdown("---")
                if not st.session_state.vocab_submitted:
                    if st.button("🚀 Nộp Bài Khảo Sát Từ Vựng", use_container_width=True):
                        v_score = sum(1 for u, c in game_answers if u == c)
                        if v_score == total_words: st.session_state.trigger_balloons = True
                        elif (v_score / total_words) >= 0.8: st.session_state.trigger_snow = True
                        st.session_state.vocab_submitted = True; st.rerun()
                else:
                    v_score = sum(1 for u, c in game_answers if u == c)
                    st.markdown(f"<div class='score-box'><h3>📊 TỔNG KẾT ĐIỂM SỐ</h3><p style='font-size: 28px; font-weight: 800; margin: 10px 0;'>Bạn thuộc: {v_score} / {total_words} Từ</p></div>", unsafe_allow_html=True)
                    if st.button("🔄 Khởi Động Lại Trận Chiến (Xuôi)", use_container_width=True):
                        st.session_state.vocab_submitted = False; st.rerun()

            # TAB 3: GAME NGƯỢC (VIỆT -> ANH)
            with tab_game_rev:
                st.markdown("### 🔄 Thử Thách Tìm Từ Tiếng Anh Đúng")
                game_rev_answers = []
                for idx, v_item in enumerate(vocabs):
                    g_word, g_meaning = v_item[0], v_item[3]
                    options = sorted(list(set([g_word] + list(set([v[0] for v in vocabs if v[0] != g_word]))[:3])))
                    with st.container(border=True):
                        st.markdown(f"🎯 Định nghĩa số {idx+1}: Nghĩa **\"{g_meaning}\"** là của từ nào?")
                        u_ans_rev = st.radio(f"Chọn từ đúng:", options, key=f"gm_rev_{g_word}", disabled=st.session_state.vocab_rev_submitted)
                        game_rev_answers.append((u_ans_rev, g_word))
                        if st.session_state.vocab_rev_submitted:
                            render_result(u_ans_rev == g_word, f"Từ tiếng Anh chuẩn xác là: **{g_word}**")
                
                st.markdown("---")
                if not st.session_state.vocab_rev_submitted:
                    if st.button("🚀 Nộp Bài Khảo Sát Ngược", use_container_width=True):
                        vr_score = sum(1 for u, c in game_rev_answers if u == c)
                        if vr_score == total_words: st.session_state.trigger_balloons = True
                        elif (vr_score / total_words) >= 0.8: st.session_state.trigger_snow = True
                        st.session_state.vocab_rev_submitted = True; st.rerun()
                else:
                    vr_score = sum(1 for u, c in game_rev_answers if u == c)
                    st.markdown(f"<div class='score-box'><h3>📊 TỔNG KẾT ĐIỂM SỐ TRẮC NGHIỆM NGƯỢC</h3><p style='font-size: 28px; font-weight: 800; margin: 10px 0;'>Bạn thuộc: {vr_score} / {total_words} Từ</p></div>", unsafe_allow_html=True)
                    if st.button("🔄 Khởi Động Lại Trận Chiến (Ngược)", use_container_width=True):
                        st.session_state.vocab_rev_submitted = False; st.rerun()

            # TAB 4: GÕ BÀN PHÍM (VIỆT -> ANH)
            with tab_input_en:
                st.markdown("### ⌨️ Đấu Trường Gõ Từ - Nhìn Nghĩa Tiếng Việt Đoán Từ Tiếng Anh")
                input_en_answers = []
                for idx, v_item in enumerate(vocabs):
                    correct_word, target_meaning = v_item[0], v_item[3]
                    with st.container(border=True):
                        st.markdown(f"🎯 Câu số {idx+1}: Gợi ý nghĩa: **\"{target_meaning}\"**")
                        u_text_en = st.text_input("Gõ từ tiếng Anh chuẩn xác tại đây:", key=f"txt_en_{correct_word}", disabled=st.session_state.text_input_en_submitted)
                        input_en_answers.append((u_text_en.strip(), correct_word))
                        if st.session_state.text_input_en_submitted:
                            render_result(u_text_en.strip().lower() == correct_word.lower(), f"Từ viết đúng là: **{correct_word}**")
                
                st.markdown("---")
                if not st.session_state.text_input_en_submitted:
                    if st.button("🚀 Chấm Điểm Bài Gõ Tiếng Anh", use_container_width=True):
                        en_score = sum(1 for u, c in input_en_answers if u.lower() == c.lower())
                        if en_score == total_words: st.session_state.trigger_balloons = True
                        st.session_state.text_input_en_submitted = True; st.rerun()
                else:
                    en_score = sum(1 for u, c in input_en_answers if u.lower() == c.lower())
                    st.markdown(f"<div class='score-box'><h3>📊 KẾT QUẢ KIỂM TRA ĐỘ CHÍNH XÁC CHÍNH TẢ</h3><p style='font-size: 24px; font-weight: 700; color: #10B981;'>Bạn viết chuẩn: {en_score} / {total_words} Từ</p></div>", unsafe_allow_html=True)
                    if st.button("🔄 Thử Sức Lại Phần Gõ Tiếng Anh", use_container_width=True):
                        st.session_state.text_input_en_submitted = False; st.rerun()

            # TAB 5: GÕ BÀN PHÍM (ANH -> VIỆT)
            with tab_input_vi:
                st.markdown("### 📝 Thử Thách Nhập Nghĩa Tiếng Việt")
                input_vi_answers = []
                for idx, v_item in enumerate(vocabs):
                    target_word, correct_meaning = v_item[0], v_item[3]
                    with st.container(border=True):
                        st.markdown(f"🎯 Từ số {idx+1}: **{target_word}**")
                        u_text_vi = st.text_input("Nhập ý nghĩa Tiếng Việt tương ứng:", key=f"txt_vi_{target_word}", disabled=st.session_state.text_input_vi_submitted)
                        
                        clean_u = u_text_vi.strip().lower()
                        clean_c = correct_meaning.strip().lower()
                        is_match = any(word in clean_c for word in clean_u.split()) if clean_u else False
                        
                        input_vi_answers.append((is_match, correct_meaning))
                        if st.session_state.text_input_vi_submitted:
                            render_result(is_match, f"Nghĩa hệ thống lưu: *{correct_meaning}*")
                
                st.markdown("---")
                if not st.session_state.text_input_vi_submitted:
                    if st.button("🚀 Kiểm Tra Giải Nghĩa Tiếng Việt", use_container_width=True):
                        st.session_state.text_input_vi_submitted = True; st.rerun()
                else:
                    vi_score = sum(1 for is_match, _ in input_vi_answers if is_match)
                    st.markdown(f"<div class='score-box'><h3>📊 TỔNG KẾT ĐIỂM GIẢI NGHĨA</h3><p style='font-size: 24px; font-weight: 700; color: #3B82F6;'>Giải nghĩa khớp: {vi_score} / {total_words} Từ</p></div>", unsafe_allow_html=True)
                    if st.button("🔄 Thử Sức Lại Phần Gõ Tiếng Việt", use_container_width=True):
                        st.session_state.text_input_vi_submitted = False; st.rerun()

            # TAB 6: FILL IN BLANK
            with tab_fill:
                st.markdown("### 📝 Thử Thách Điền Từ Vào Chỗ Trống")
                input_answers = []
                for idx, v_item in enumerate(vocabs):
                    f_word, f_context = v_item[8], v_item[0]
                    with st.container(border=True):
                        st.markdown(f"**Câu hỏi {idx+1}:** {hide_keyword_for_exercise(f_word, f_context)}")
                        u_input = st.text_input("Nhập từ tiếng Anh còn thiếu:", key=f"fill_{f_context}", disabled=st.session_state.fill_blank_submitted)
                        input_answers.append((f_context, u_input.strip()))
                
                st.markdown("---")
                if not st.session_state.fill_blank_submitted:
                    if st.button("🚀 Kiểm Tra Đáp Án Điền Từ", use_container_width=True):
                        f_score = sum(1 for f_w, u_in in input_answers if u_in.lower() == f_w.lower())
                        if f_score == total_words: st.session_state.trigger_balloons = True
                        elif (f_score / total_words) >= 0.8: st.session_state.trigger_snow = True
                        st.session_state.fill_blank_submitted = True; st.rerun()
                else:
                    for f_word, u_input in input_answers:
                        if u_input.lower() == f_word.lower(): st.success(f"✅ Đúng: Từ **{f_word}**")
                        else: st.error(f"❌ Chưa đúng -> Từ khóa chính xác: **{f_word}** (Bạn gõ: '{u_input}')")
                    if st.button("🔄 Làm Lại Thử Thách Điền Từ", use_container_width=True):
                        st.session_state.fill_blank_submitted = False; st.rerun()

# --- TRUNG TÂM ADMIN ---
elif choice == "⚙️ Trung Tâm Admin":
    st.title("⚙️ Trung Tâm Admin")
    t1, t2, t3, t4 = st.tabs(["👥 Thành Viên", "📂 Sửa/Xóa Bài", "📚 Nạp Bài Mới", "🧠 Nạp Từ Vựng Lớn"])
    
    with t1:
        st.subheader("👥 Quản Lý Thành Viên & Sao Lưu Dữ Liệu")
        with st.expander("💾 Trung Tâm Sao Lưu & Phục Hồi", expanded=False):
            col_bk1, col_bk2 = st.columns(2)
            with col_bk1:
                if st.button("Tạo Bản Sao Lưu Hệ Thống 📦", use_container_width=True):
                    try:
                        conn = sqlite3.connect(DB_NAME)
                        u_data = [dict(zip(["username", "password", "role", "allow_reading_part", "allow_vocab_part"], r)) for r in conn.execute("SELECT username, password, role, allow_reading_part, allow_vocab_part FROM users").fetchall()]
                        l_data = [dict(zip(["level", "title", "content", "grammar_points", "quiz"], r)) for r in conn.execute("SELECT level, title, content, grammar_points, quiz FROM reading_lessons").fetchall()]
                        v_data = [dict(zip(["vocab_date", "word", "word_type", "phonetic", "meaning", "prefix", "suffix", "funny_story", "other_forms", "context_easy", "context_medium", "context_hard"], r)) for r in conn.execute("SELECT vocab_date, word, word_type, phonetic, meaning, prefix, suffix, funny_story, other_forms, context_easy, context_medium, context_hard FROM vocabulary").fetchall()]
                        conn.close()
                        
                        st.download_button(
                            label="📥 Tải File Backup (.json) Về Máy",
                            data=json.dumps({"users": u_data, "reading_lessons": l_data, "vocabulary": v_data}, ensure_ascii=False, indent=4),
                            file_name=f"english4today_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json", use_container_width=True
                        )
                    except Exception as e: st.error(f"Lỗi sao lưu: {e}")
                        
            with col_bk2:
                uploaded_backup_file = st.file_uploader("Chọn file backup (.json):", type=["json"], key="restore_uploader")
                if uploaded_backup_file and st.button("🔥 Tiến Hành Khôi Phục Dữ Liệu", use_container_width=True, type="primary"):
                    try:
                        data = json.load(uploaded_backup_file)
                        conn = sqlite3.connect(DB_NAME)
                        if "users" in data:
                            for u in data["users"]: conn.execute("INSERT OR IGNORE INTO users (username, password, role, allow_reading_part, allow_vocab_part) VALUES (?,?,?,?,?)", (u["username"], u["password"], u["role"], u["allow_reading_part"], u["allow_vocab_part"]))
                        if "reading_lessons" in data:
                            conn.execute("DELETE FROM reading_lessons")
                            for l in data["reading_lessons"]: conn.execute("INSERT INTO reading_lessons (level, title, content, grammar_points, quiz) VALUES (?,?,?,?,?)", (l["level"], l["title"], l["content"], l["grammar_points"], l["quiz"]))
                        if "vocabulary" in data:
                            conn.execute("DELETE FROM vocabulary")
                            for v in data["vocabulary"]: conn.execute("INSERT INTO vocabulary (vocab_date, word, word_type, phonetic, meaning, prefix, suffix, funny_story, other_forms, context_easy, context_medium, context_hard) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", (v["vocab_date"], v["word"], v["word_type"], v["phonetic"], v["meaning"], v["prefix"], v["suffix"], v["funny_story"], v["other_forms"], v["context_easy"], v["context_medium"], v["context_hard"]))
                        conn.commit(); conn.close(); st.success("🎉 Khôi phục dữ liệu thành công!"); st.rerun()
                    except Exception as e: st.error(f"Lỗi: {e}")

        st.markdown("---")
        col_u1, col_u2 = st.columns([1.2, 2])
        with col_u1:
            st.markdown("#### ➕ Thêm Học Viên Mới")
            with st.form("add_new_user_form", clear_on_submit=True):
                new_u = st.text_input("Tên tài khoản mới:").strip()
                new_p = st.text_input("Mật khẩu tài khoản:", type="password").strip()
                r_perm = st.checkbox("Quyền Bài Đọc", value=True)
                v_perm = st.checkbox("Quyền Từ Vựng", value=True)
                if st.form_submit_button("Lưu Học Viên 💾", use_container_width=True):
                    if new_u and new_p:
                        conn = sqlite3.connect(DB_NAME)
                        try:
                            conn.execute("INSERT INTO users (username, password, role, allow_reading_part, allow_vocab_part) VALUES (?, ?, 'user', ?, ?)", (new_u, new_p, int(r_perm), int(v_perm)))
                            conn.commit(); st.success(f"🎉 Tạo tài khoản thành công!"); st.rerun()
                        except sqlite3.IntegrityError: st.error("❌ Tài khoản đã tồn tại!")
                        finally: conn.close()
                    else: st.error("❌ Điền thiếu thông tin!")

        with col_u2:
            st.markdown("#### 📋 Danh Sách Học Viên Hiện Có")
            conn = sqlite3.connect(DB_NAME)
            all_users = conn.execute("SELECT user_id, username, password, allow_reading_part, allow_vocab_part FROM users WHERE role != 'admin'").fetchall()
            conn.close()
            for u_id, username, password, allow_r, allow_v in all_users:
                with st.container(border=True):
                    st.markdown(f"👤 Học viên: **{username}** (MK: `{password}`)")
                    c1, c2, c3 = st.columns(3)
                    if c1.checkbox("Quyền Bài Đọc", value=bool(allow_r), key=f"user_r_{u_id}") != bool(allow_r):
                        conn = sqlite3.connect(DB_NAME); conn.execute("UPDATE users SET allow_reading_part = ? WHERE user_id = ?", (int(not allow_r), u_id)); conn.commit(); conn.close(); st.rerun()
                    if c2.checkbox("Quyền Từ Vựng", value=bool(allow_v), key=f"user_v_{u_id}") != bool(allow_v):
                        conn = sqlite3.connect(DB_NAME); conn.execute("UPDATE users SET allow_vocab_part = ? WHERE user_id = ?", (int(not allow_v), u_id)); conn.commit(); conn.close(); st.rerun()
                    if c3.button("Xóa 🗑️", key=f"del_user_{u_id}", use_container_width=True):
                        conn = sqlite3.connect(DB_NAME); conn.execute("DELETE FROM users WHERE user_id = ?", (u_id,)); conn.commit(); conn.close(); st.rerun()

    with t2:
        st.subheader("🛠️ Trung Tâm Biên Tập Ngữ Liệu")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.markdown("#### 📚 Quản lý Bài Đọc")
            conn = sqlite3.connect(DB_NAME); r_lessons = conn.execute("SELECT id, title, level, content FROM reading_lessons").fetchall(); conn.close()
            for r_id, r_title, r_lvl, r_content in r_lessons:
                with st.container(border=True):
                    st.write(f"**[{r_lvl}] {r_title}**")
                    c1, c2 = st.columns(2)
                    with c1.popover("Sửa ✏️", use_container_width=True):
                        with st.form(f"edit_read_{r_id}"):
                            e_title = st.text_input("Tiêu đề:", value=r_title)
                            e_lvl = st.text_input("Cấp độ:", value=r_lvl)
                            e_content = st.text_area("Nội dung:", value=r_content)
                            if st.form_submit_button("Cập nhật 💾"):
                                conn = sqlite3.connect(DB_NAME); conn.execute("UPDATE reading_lessons SET title=?, level=?, content=? WHERE id=?", (e_title, e_lvl, e_content, r_id)); conn.commit(); conn.close(); st.rerun()
                    if c2.button("Xóa 🗑️", key=f"del_read_{r_id}", use_container_width=True):
                        conn = sqlite3.connect(DB_NAME); conn.execute("DELETE FROM reading_lessons WHERE id=?", (r_id,)); conn.commit(); conn.close(); st.rerun()
        with col_m2:
            st.markdown("#### 🧠 Quản lý Từ Vựng")
            conn = sqlite3.connect(DB_NAME); v_words = conn.execute("SELECT id, word, vocab_date, meaning, funny_story FROM vocabulary ORDER BY vocab_date DESC").fetchall(); conn.close()
            for v_id, v_word, v_dt, v_meaning, v_story in v_words:
                with st.container(border=True):
                    st.write(f"📆 *{v_dt}* - **{v_word}** ({v_meaning})")
                    c1, c2 = st.columns(2)
                    with c1.popover("Sửa ✏️", use_container_width=True):
                        with st.form(f"edit_voc_{v_id}"):
                            e_word = st.text_input("Từ:", value=v_word)
                            e_meaning = st.text_input("Nghĩa:", value=v_meaning)
                            e_story = st.text_area("Mẹo:", value=v_story)
                            if st.form_submit_button("Lưu 💾"):
                                conn = sqlite3.connect(DB_NAME); conn.execute("UPDATE vocabulary SET word=?, meaning=?, funny_story=? WHERE id=?", (e_word, e_meaning, e_story, v_id)); conn.commit(); conn.close(); st.rerun()
                    if c2.button("Xóa 🗑️", key=f"del_voc_{v_id}", use_container_width=True):
                        conn = sqlite3.connect(DB_NAME); conn.execute("DELETE FROM vocabulary WHERE id=?", (v_id,)); conn.commit(); conn.close(); st.rerun()

    with t3:
        st.subheader("Nạp Bài Đọc Mới")
        js_r = st.text_area("Dán JSON bài đọc:", height=150)
        if st.button("Lưu bài đọc") and js_r.strip():
            try:
                d = json.loads(js_r.strip())
                conn = sqlite3.connect(DB_NAME); conn.execute("INSERT INTO reading_lessons (level, title, content, grammar_points, quiz) VALUES (?,?,?,?,?)", (d.get("level","A1"), d.get("title",""), d.get("content",""), json.dumps(d.get("grammar_points",[])), json.dumps(d.get("quiz",[])))); conn.commit(); conn.close(); st.rerun()
            except Exception as e: st.error(f"Lỗi: {e}")

    with t4:
        st.subheader("Nạp Từ Vựng Lớn")
        js_v = st.text_area("Dán Mảng JSON từ vựng:", height=150)
        if st.button("Đóng gói nạp hàng loạt") and js_v.strip():
            try:
                v_list = json.loads(js_v.strip())
                conn = sqlite3.connect(DB_NAME)
                for item in v_list:
                    conn.execute("INSERT OR REPLACE INTO vocabulary (vocab_date, word, word_type, phonetic, meaning, prefix, suffix, funny_story, other_forms, context_easy, context_medium, context_hard) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", (item.get('date', datetime.now().strftime('%Y-%m-%d')), item['word'], item.get('word_type',''), item['phonetic'], item['meaning'], item.get('prefix',''), item.get('suffix',''), item['funny_story'], item.get('other_forms',''), item['context_easy'], item['context_medium'], item['context_hard']))
                conn.commit(); conn.close(); st.rerun()
            except Exception as e: st.error(f"Lỗi: {e}")