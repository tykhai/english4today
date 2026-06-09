import streamlit as st
import sqlite3
import json
import re
from datetime import datetime

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="English4Today - Học Gây Nghiện", page_icon="⚡", layout="wide")

# --- CUSTOM CSS (MÀU SẮC SINH ĐỘNG, TRỰC QUAN) ---
st.markdown("""
<style>
    .main-header { font-size:34px !important; font-weight: 800; color: #1E3A8A; text-align: center; margin-bottom: 25px; }
    .flashcard { background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%); padding: 30px; border-radius: 20px; border-left: 8px solid #4F46E5; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05); margin-bottom: 20px; }
    .story-card { background-color: #FFFBEB; padding: 18px; border-radius: 12px; border: 1px dashed #F59E0B; font-style: italic; }
    .progress-text { font-size: 18px; font-weight: bold; color: #4F46E5; text-align: center; margin-bottom: 10px; }
    .score-box { padding: 25px; border-radius: 20px; text-align: center; margin-top: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border: 2px solid #E2E8F0; }
    .q-result { padding: 8px 12px; border-radius: 6px; margin-top: 8px; font-weight: bold; font-size: 14px; display: inline-block; }
</style>
""", unsafe_allow_html=True)

# --- KHỞI TẠO CƠ SỞ DỮ LIỆU ---
def init_db():
    conn = sqlite3.connect("english_learning.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, role TEXT, allow_reading_part INTEGER DEFAULT 1, allow_vocab_part INTEGER DEFAULT 1)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS reading_lessons (id INTEGER PRIMARY KEY AUTOINCREMENT, level TEXT, title TEXT, content TEXT, grammar_points TEXT, quiz TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS vocabulary (id INTEGER PRIMARY KEY AUTOINCREMENT, vocab_date TEXT, word TEXT UNIQUE, word_type TEXT, phonetic TEXT, meaning TEXT, prefix TEXT, suffix TEXT, funny_story TEXT, other_forms TEXT, context_easy TEXT, context_medium TEXT, context_hard TEXT)''')
    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin')")
        conn.commit()
    except sqlite3.IntegrityError: pass
    conn.close()

init_db()

# --- HÀM PHÁT ÂM CHUẨN NATIVE (CẬP NHẬT ST.HTML CHUẨN 2026) ---
def execute_speech(text_to_speak):
    clean_text = text_to_speak.replace("'", "\\'").replace("\n", " ").replace("**", "")
    js_code = f"""
    <iframe srcdoc="
        <script>
            window.speechSynthesis.cancel();
            let u = new SpeechSynthesisUtterance('{clean_text}');
            u.lang = 'en-US'; u.rate = 0.85;
            window.speechSynthesis.speak(u);
        </script>
    " style="display:none; width:0; height:0; border:none;"></iframe>
    """
    st.html(js_code)

# --- HÀM DỌN DẸP VÀ IN ĐẬM TỪ KHÓA CHUẨN XÁC VỚI MARKDOWN ---
def clean_and_bold_keyword(sentence, keyword):
    if not sentence: return ""
    clean_sentence = sentence.replace("**", "").replace("*", "")
    pattern = re.compile(re.escape(keyword), re.IGNORECASE)
    return pattern.sub(f"**{keyword}**", clean_sentence)

# --- HÀM ẨN TỪ KHÓA ĐỂ LÀM BÀI TẬP ĐIỀN TỪ ---
def hide_keyword_for_exercise(sentence, keyword):
    if not sentence: return ""
    clean_sentence = sentence.replace("**", "").replace("*", "")
    pattern = re.compile(re.escape(keyword), re.IGNORECASE)
    return pattern.sub("_______", clean_sentence)

# --- KHỞI TẠO BIẾN TRẠNG THÁI (SESSION STATE) ---
if "user" not in st.session_state: st.session_state.user = None
if "vocab_index" not in st.session_state: st.session_state.vocab_index = 0
if "current_date" not in st.session_state: st.session_state.current_date = ""

if "reading_submitted" not in st.session_state: st.session_state.reading_submitted = False
if "vocab_submitted" not in st.session_state: st.session_state.vocab_submitted = False
if "fill_blank_submitted" not in st.session_state: st.session_state.fill_blank_submitted = False

# --- GIAO DIỆN ĐĂNG NHẬP ---
if st.session_state.user is None:
    st.markdown("<div class='main-header'>🚀 English4Today - Hệ Thống Học Ngữ Liệu Gây Nghiện</div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.3, 1])
    with col2:
        with st.container(border=True):
            username = st.text_input("Tài khoản:")
            password = st.text_input("Mật khẩu:", type="password")
            if st.button("🔥 Tiến Vào Đấu Trường Học Tập", use_container_width=True):
                conn = sqlite3.connect("english_learning.db")
                cursor = conn.cursor()
                cursor.execute("SELECT username, role, allow_reading_part, allow_vocab_part FROM users WHERE username=? AND password=?", (username.strip(), password.strip()))
                res = cursor.fetchone()
                conn.close()
                if res:
                    st.session_state.user = {"username": res[0], "role": res[1], "allow_reading": res[2], "allow_vocab": res[3]}
                    st.rerun()
                else: st.error("❌ Sai tài khoản hoặc mật khẩu!")
    st.stop()

user = st.session_state.user

# --- NAVIGATION SIDEBAR ---
with st.sidebar:
    st.markdown(f"### 🎉 Chiến binh: **{user['username']}**")
    st.markdown("---")
    menu = []
    if user['allow_reading'] or user['role'] == 'admin': menu.append("📚 Thử Thách Bài Đọc")
    if user['allow_vocab'] or user['role'] == 'admin': menu.append("🧠 Từ Vựng Theo Ngày")
    if user['role'] == 'admin': menu.append("⚙️ Trung Tâm Admin")
    choice = st.radio("Lộ trình hằng ngày:", menu)
    st.markdown("---")
    if st.button("Đăng xuất 🚪", use_container_width=True):
        st.session_state.user = None
        st.rerun()

# --- PHẦN 1: THỬ THÁCH BÀI ĐỌC ---
if choice == "📚 Thử Thách Bài Đọc":
    st.markdown("<div class='main-header'>📚 Luyện Ngữ Liệu & Thử Thách Đọc Hiểu</div>", unsafe_allow_html=True)
    conn = sqlite3.connect("english_learning.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, level, title, content, grammar_points, quiz FROM reading_lessons")
    lessons = cursor.fetchall()
    conn.close()

    if not lessons: st.info("Chưa có bài đọc nào trong DB.")
    else:
        levels = sorted(list(set([r[1] for r in lessons])))
        selected_lvl = st.segmented_control("Chọn cấp độ trình độ:", levels, default=levels[0])
        filtered = [l for l in lessons if l[1] == selected_lvl]
        
        if filtered:
            titles = [l[2] for l in filtered]
            sel_title = st.selectbox("Chọn bài viết mục tiêu:", titles)
            cur_lesson = [l for l in filtered if l[2] == sel_title][0]
            l_id, lvl, title, content, grammar_points, quiz_json = cur_lesson
            
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1: st.markdown(f"### 📖 {title}")
                with col2:
                    if st.button("🔊 Đọc Toàn Bộ Bài Văn", use_container_width=True):
                        execute_speech(content)
                
                st.markdown(f"<div style='background-color: #F0FDF4; padding: 20px; border-radius: 12px; font-size: 18px; color: #1E293B; line-height: 1.7; border-left: 4px solid #10B981; margin-bottom: 15px;'>{content}</div>", unsafe_allow_html=True)
                
                with st.expander("💡 Xem Cấu Trúc Ngữ Pháp Chuyên Sâu"):
                    if grammar_points:
                        try:
                            g_data = json.loads(grammar_points)
                            for g in g_data:
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
                                    if ans == q['answer']:
                                        st.markdown("<div class='q-result' style='background-color: #DCFCE7; color: #14532D;'>🟢 CHÍNH XÁC!</div>", unsafe_allow_html=True)
                                    else:
                                        st.markdown(f"<div class='q-result' style='background-color: #FEE2E2; color: #7F1D1D;'>❌ CHƯA ĐÚNG -> Đáp án chuẩn là: {q['answer']}</div>", unsafe_allow_html=True)
                        
                        st.markdown("---")
                        if not st.session_state.reading_submitted:
                            if st.button("🚀 Nộp Bài & Chấm Điểm Bài Đọc", use_container_width=True):
                                # Kích hoạt hiệu ứng ngay lúc bắt đầu nộp bài dựa theo điểm số
                                score_test = sum(1 for idx, q in enumerate(quizzes) if user_answers[idx] == q['answer'])
                                ratio_test = score_test / len(quizzes)
                                if score_test == len(quizzes): st.balloons()
                                elif ratio_test >= 0.8: st.snow()
                                
                                st.session_state.reading_submitted = True
                                st.rerun()
                        else:
                            score = sum(1 for idx, q in enumerate(quizzes) if user_answers[idx] == q['answer'])
                            total_q = len(quizzes)
                            ratio = score / total_q
                            
                            if score == total_q:
                                bg_color, border_color, text_color = "#ECFDF5", "#10B981", "#064E3B"
                                comment = "🔥 Tuyệt đỉnh thiên tài! Bạn đã thấu hiểu hoàn toàn 100% ngữ cảnh bài đọc này!"
                            elif ratio >= 0.8:
                                bg_color, border_color, text_color = "#EFF6FF", "#3B82F6", "#1E3A8A"
                                comment = "🌟 Xuất sắc! Bộ não của bạn bắt nhịp ngữ liệu rất nhanh, giữ vững phong độ nhé!"
                            elif ratio < 0.5:
                                bg_color, border_color, text_color = "#FFF7ED", "#F97316", "#7C2D12"
                                comment = "💪 Đừng nản lòng nhé! Tiếng Anh cần sự tích lũy, hãy bấm 'Làm lại' để đọc kỹ và chinh phục lại câu hỏi nào!"
                            else:
                                bg_color, border_color, text_color = "#F8FAFC", "#94A3B8", "#1E293B"
                                comment = "👍 Khá tốt! Bạn đã vượt qua mức trung bình. Học thêm vài cấu trúc để đạt điểm tối đa ở lần tới!"

                            st.markdown(f"""
                            <div class='score-box' style='background: {bg_color}; border: 2px solid {border_color}; color: {text_color};'>
                                <h3>🏆 KẾT QUẢ TỔNG KẾT ĐẤU TRƯỜNG</h3>
                                <p style='font-size: 28px; font-weight: 800; margin: 10px 0;'>Bạn đạt: {score} / {total_q} Câu đúng</p>
                                <p style='font-size: 16px; font-weight: 600;'>💡 Lời khuyên: {comment}</p>
                            </div>
                            """, unsafe_allow_html=True)
                                
                            if st.button("🔄 Làm Lại Bài Đọc Này", use_container_width=True):
                                st.session_state.reading_submitted = False
                                st.rerun()
                                
                    except Exception as e: st.write("Chưa có bộ câu hỏi trắc nghiệm chuẩn.")

# --- PHẦN 2: TỪ VỰNG THEO NGÀY ---
elif choice == "🧠 Từ Vựng Theo Ngày":
    st.markdown("<div class='main-header'>🧠 Sổ Tay Từ Vựng Thông Minh Theo Ngày</div>", unsafe_allow_html=True)
    conn = sqlite3.connect("english_learning.db")
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT TRIM(vocab_date) FROM vocabulary ORDER BY vocab_date DESC")
    dates = [r[0] for r in cursor.fetchall()]
    conn.close()

    if not dates: st.info("Chưa có từ vựng nào được nạp.")
    else:
        selected_date = st.selectbox("📆 Chọn ngày học tập mục tiêu:", dates)
        
        if st.session_state.current_date != selected_date:
            st.session_state.vocab_index = 0
            st.session_state.current_date = selected_date
            st.session_state.vocab_submitted = False
            st.session_state.fill_blank_submitted = False
            
        conn = sqlite3.connect("english_learning.db")
        cursor = conn.cursor()
        cursor.execute("SELECT word, word_type, phonetic, meaning, prefix, suffix, funny_story, other_forms, context_easy, context_medium, context_hard FROM vocabulary WHERE TRIM(vocab_date)=?", (selected_date,))
        vocabs = cursor.fetchall()
        conn.close()
        
        total_words = len(vocabs)
        
        if total_words > 0:
            tab_learn, tab_game, tab_fill = st.tabs(["🌟 Chế Độ Học Thẻ Flashcard", "⚔️ Trận Chiến Trắc Nghiệm Nghĩa", "📝 Thử Thách Điền Từ Vào Câu"])
            
            # --- CHẾ ĐỘ HỌC FLASHCARD (SỬA LỖI IN ĐẬM) ---
            with tab_learn:
                idx = st.session_state.vocab_index
                st.markdown(f"<div class='progress-text'>⚡ TIẾN ĐỘ: Từ {idx+1} / {total_words} (Ngày {selected_date})</div>", unsafe_allow_html=True)
                st.progress((idx + 1) / total_words)
                
                word, w_type, phonetic, meaning, prefix, suffix, story, other_forms, c_easy, c_medium, c_hard = vocabs[idx]
                
                with st.container():
                    st.markdown(f"""
                    <div class='flashcard'>
                        <span style='font-size:36px; font-weight:bold; color:#4F46E5;'>{word}</span> 
                        <span style='background-color:#EEF2F6; color:#64748B; font-size:14px; padding:4px 8px; border-radius:6px;'>{w_type.upper()}</span>
                        <p style='font-size: 18px; margin-top:10px;'>🗣️ Phiên âm: <code>{phonetic}</code> | <strong>Ý nghĩa: {meaning}</strong></p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("🔊 Phát Âm Từ Này", key=f"spk_{word}"):
                        execute_speech(word)
                
                col_l, col_r = st.columns([1, 1])
                with col_l:
                    st.markdown(f"<div class='story-card'><strong>💡 Mẹo kể chuyện liên tưởng:</strong><br><br>{story}</div>", unsafe_allow_html=True)
                    st.markdown("#### 🗺️ Bản Đồ Cấu Trúc Từ (Word Mindmap)")
                    mm_text = f"🌟 Từ Khóa: {word} ({w_type})\n"
                    mm_text += f"├── 🧬 Tiền tố (Prefix): {prefix if prefix else 'N/A'}\n"
                    mm_text += f"├── 🧬 Hậu tố (Suffix): {suffix if suffix else 'N/A'}\n"
                    mm_text += f"└── 🌿 Gia đình từ (Word Family):\n"
                    if other_forms:
                        for line in other_forms.split('\n'): mm_text += f"    {line}\n"
                    st.code(mm_text, language="text")
                    
                with col_r:
                    st.markdown("#### 🧬 Các Loại Từ Liên Quan (Word Forms)")
                    st.info(other_forms if other_forms else "Chưa bổ sung.")
                    
                    # SỬA LỖI IN ĐẬM TRỰC QUAN BẰNG MARKDOWN NGUYÊN BẢN CỦA STREAMLIT
                    st.markdown("#### 🎯 Ngữ Cảnh Ứng Dụng")
                    st.write("🟢 **Dễ:**", clean_and_bold_keyword(c_easy, word))
                    st.write("🔵 **Vừa:**", clean_and_bold_keyword(c_medium, word))
                    st.write("🔴 **Khó:**", clean_and_bold_keyword(c_hard, word))

                st.markdown("---")
                col_prev, col_space, col_next = st.columns([1, 2, 1])
                with col_prev:
                    if st.button("⬅️ Từ Trước Đó", use_container_width=True, disabled=(idx == 0)):
                        st.session_state.vocab_index -= 1
                        st.rerun()
                with col_next:
                    if st.button("Từ Tiếp Theo ➡️", use_container_width=True, disabled=(idx == total_words - 1)):
                        st.session_state.vocab_index += 1
                        st.rerun()

            # --- CHẾ ĐỘ TRẬN CHIẾN TRẮC NGHIỆM CHUẨN HIỆU ỨNG ---
            with tab_game:
                st.markdown("### ⚔️ Thử Thách Trí Nhớ - Chọn Nghĩa Đúng Của Từ")
                
                game_answers = []
                for idx, v_item in enumerate(vocabs):
                    g_word = v_item[0]
                    g_correct_meaning = v_item[3]
                    
                    other_meanings = list(set([v[3] for v in vocabs if v[3] != g_correct_meaning]))[:3]
                    options = list(set([g_correct_meaning] + other_meanings))
                    options.sort()
                    
                    with st.container(border=True):
                        st.markdown(f"🎯 Từ số {idx+1}: **{g_word}** nghĩa là gì?")
                        u_ans = st.radio(f"Chọn đáp án:", options, key=f"gm_v_{g_word}", disabled=st.session_state.vocab_submitted)
                        game_answers.append((g_word, u_ans, g_correct_meaning))
                        
                        if st.session_state.vocab_submitted:
                            if u_ans == g_correct_meaning:
                                st.markdown("<div class='q-result' style='background-color: #DCFCE7; color: #14532D;'>🟢 CHÍNH XÁC!</div>", unsafe_allow_html=True)
                            else:
                                st.markdown(f"<div class='q-result' style='background-color: #FEE2E2; color: #7F1D1D;'>❌ CHƯA ĐÚNG -> Nghĩa chuẩn xác là: {g_correct_meaning}</div>", unsafe_allow_html=True)
                
                st.markdown("---")
                if not st.session_state.vocab_submitted:
                    if st.button("🚀 Nộp Bài Khảo Sát Từ Vựng", use_container_width=True):
                        # Tính điểm nhanh kích hoạt hiệu ứng pháo hoa ngay lập tức trước rerun
                        v_score_test = sum(1 for g_word, u_ans, g_correct in game_answers if u_ans == g_correct)
                        v_ratio_test = v_score_test / total_words
                        if v_score_test == total_words: st.balloons()
                        elif v_ratio_test >= 0.8: st.snow()
                        
                        st.session_state.vocab_submitted = True
                        st.rerun()
                else:
                    v_score = sum(1 for g_word, u_ans, g_correct in game_answers if u_ans == g_correct)
                    v_ratio = v_score / total_words
                    
                    if v_score == total_words:
                        b_bg, b_border, b_text = "#ECFDF5", "#10B981", "#064E3B"
                        b_comment = "🏆 Bộ não bách phát bách trúng! Bạn đã thuộc làu không sót một từ nào của ngày hôm nay!"
                    elif v_ratio >= 0.8:
                        b_bg, b_border, b_text = "#EFF6FF", "#3B82F6", "#1E3A8A"
                        b_comment = "🌟 Quá xuất sắc! Bạn nhớ được hầu hết lượng từ vựng nâng cao rồi đó!"
                    elif v_ratio < 0.5:
                        b_bg, b_border, b_text = "#FFF7ED", "#F97316", "#7C2D12"
                        b_comment = "💪 Đừng lo lắng! Hãy lật lại thẻ Flashcard lướt qua mẹo liên tưởng một lần nữa, từ vựng sẽ tự găm vào đầu bạn thôi!"
                    else:
                        b_bg, b_border, b_text = "#F8FAFC", "#94A3B8", "#1E293B"
                        b_comment = "👍 Bạn đã đi được nửa chặng đường thành công rồi. Làm lại một lần nữa để đạt điểm tối đa!"

                    st.markdown(f"""
                    <div class='score-box' style='background: {b_bg}; border: 2px solid {b_border}; color: {b_text};'>
                        <h3>📊 TỔNG KẾT ĐIỂM SỐ TỪ VỰNG</h3>
                        <p style='font-size: 28px; font-weight: 800; margin: 10px 0;'>Bạn thuộc: {v_score} / {total_words} Từ</p>
                        <p style='font-size: 16px; font-weight: 600;'>💡 Nhận xét: {b_comment}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("🔄 Khởi Động Lại Trận Chiến", use_container_width=True):
                        st.session_state.vocab_submitted = False
                        st.rerun()

            # --- CHẾ ĐỘ THỬ THÁCH ĐIỀN TỪ ---
            with tab_fill:
                st.markdown("### 📝 Thử Thách Tư Duy - Điền Từ Thích Hợp Vào Chỗ Trống")
                
                input_answers = []
                for idx, v_item in enumerate(vocabs):
                    f_word = v_item[0]
                    f_context = v_item[8]
                    hidden_sentence = hide_keyword_for_exercise(f_context, f_word)
                    
                    with st.container(border=True):
                        st.markdown(f"**Câu hỏi {idx+1}:** {hidden_sentence}")
                        user_input = st.text_input("Nhập từ tiếng Anh còn thiếu:", key=f"fill_{f_word}", disabled=st.session_state.fill_blank_submitted)
                        input_answers.append((f_word, user_input.strip()))
                
                st.markdown("---")
                if not st.session_state.fill_blank_submitted:
                    if st.button("🚀 Kiểm Tra Đáp An Điền Từ", use_container_width=True):
                        f_score_test = sum(1 for f_word, u_input in input_answers if u_input.lower() == f_word.lower())
                        f_ratio_test = f_score_test / total_words
                        if f_score_test == total_words: st.balloons()
                        elif f_ratio_test >= 0.8: st.snow()
                        
                        st.session_state.fill_blank_submitted = True
                        st.rerun()
                else:
                    f_score = 0
                    for f_word, u_input in input_answers:
                        if u_input.lower() == f_word.lower():
                            st.success(f"✅ Đúng: Từ **{f_word}**")
                            f_score += 1
                        else:
                            st.error(f"❌ Chưa đúng -> Từ khóa chuẩn phải là: **{f_word}** (Bạn nhập: '{u_input}')")
                            
                    f_ratio = f_score / total_words
                    if f_score == total_words:
                        f_bg, f_border, f_text = "#ECFDF5", "#10B981", "#064E3B"
                        f_comment = "🏅 Vô địch điền từ! Khả năng nhớ và viết chính xác ngữ cảnh của bạn quá đỉnh cao!"
                    elif f_ratio >= 0.8:
                        f_bg, f_border, f_text = "#EFF6FF", "#3B82F6", "#1E3A8A"
                        f_comment = "🌟 Tuyệt vời! Bạn chỉ sai sót một chút lỗi chính tả nhỏ thôi, tổng quan rất tốt!"
                    elif f_ratio < 0.5:
                        f_bg, f_border, f_text = "#FFF7ED", "#F97316", "#7C2D12"
                        f_comment = "💪 Gõ lại một lần nữa là nhớ ngay ấy mà! Hãy bấm nút làm lại bên dưới để luyện cơ tay và trí óc."
                    else:
                        f_bg, f_border, f_text = "#F8FAFC", "#94A3B8", "#1E293B"
                        f_comment = "👍 Bạn đã nắm được cốt lõi bài học. Thử sức lại để hoàn thành mục tiêu 100% nhé!"

                    st.markdown(f"""
                    <div class='score-box' style='background: {f_bg}; border: 2px solid {f_border}; color: {f_text};'>
                        <h3>📊 KẾT QUẢ ĐIỀN TỪ NGỮ CẢNH</h3>
                        <p style='font-size: 28px; font-weight: 800; margin: 10px 0;'>Chính xác: {f_score} / {total_words} Câu</p>
                        <p style='font-size: 16px; font-weight: 600;'>💡 Lời khuyên: {f_comment}</p>
                    </div>
                    """, unsafe_allow_html=True)
                        
                    if st.button("🔄 Làm Lại Thử Thách Điền Từ", use_container_width=True):
                        st.session_state.fill_blank_submitted = False
                        st.rerun()

# --- TRUNG TÂM ADMIN ---
elif choice == "⚙️ Trung Tâm Admin":
    st.title("⚙️ Trung Tâm Admin")
    t1, t2, t3, t4 = st.tabs(["👥 Thành Viên", "📂 Sửa/Xóa Bài", "📝 Nạp Bài Đọc Mới", "🧠 Nạp Từ Vựng Lớn"])
    
    with t1:
        st.subheader("Quản Lý Thành Viên")
        with st.form("add_u"):
            u = st.text_input("Tên tài khoản mới:")
            p = st.text_input("Mật khẩu:")
            if st.form_submit_button("Lưu Học Viên"):
                if u and p:
                    try:
                        conn = sqlite3.connect("english_learning.db")
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO users (username, password, role) VALUES (?,?,'user')",(u.strip(), p.strip()))
                        conn.commit(); conn.close()
                        st.success("Tạo thành công!"); st.rerun()
                    except: st.error("Tài khoản đã tồn tại!")
    with t2:
        st.subheader("Xóa Ngữ Liệu Thô")
        conn = sqlite3.connect("english_learning.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, title FROM reading_lessons")
        rl = cursor.fetchall()
        cursor.execute("SELECT id, word FROM vocabulary")
        vl = cursor.fetchall()
        conn.close()
        for rid, rtit in rl:
            if st.button(f"🗑️ Xóa bài: {rtit}", key=f"del_r_{rid}"):
                conn = sqlite3.connect("english_learning.db")
                cursor = conn.cursor(); cursor.execute("DELETE FROM reading_lessons WHERE id=?",(rid,)); conn.commit(); conn.close()
                st.rerun()
        for vid, vwd in vl:
            if st.button(f"🗑️ Xóa từ: {vwd}", key=f"del_v_{vid}"):
                conn = sqlite3.connect("english_learning.db")
                cursor = conn.cursor(); cursor.execute("DELETE FROM vocabulary WHERE id=?",(vid,)); conn.commit(); conn.close()
                st.rerun()
    with t3:
        st.subheader("Nạp Bài Đọc Mới")
        js_r = st.text_area("Dán JSON bài đọc tại đây:", height=200)
        if st.button("Lưu bài đọc"):
            if js_r.strip():
                try:
                    d = json.loads(js_r.strip())
                    conn = sqlite3.connect("english_learning.db")
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO reading_lessons (level, title, content, grammar_points, quiz) VALUES (?,?,?,?,?)",
                                   (d.get("level","A1"), d.get("title",""), d.get("content",""), json.dumps(d.get("grammar_points",[])), json.dumps(d.get("quiz",[]))))
                    conn.commit(); conn.close()
                    st.success("Đã nạp bài đọc!"); st.rerun()
                except Exception as e: st.error(f"Lỗi JSON: {e}")
    with t4:
        st.subheader("Nạp Từ Vựng Lớn")
        js_v = st.text_area("Dán Mảng JSON từ vựng tại đây:", height=200)
        if st.button("Đóng gói nạp hàng loạt"):
            if js_v.strip():
                try:
                    v_list = json.loads(js_v.strip())
                    conn = sqlite3.connect("english_learning.db")
                    cursor = conn.cursor()
                    for item in v_list:
                        cursor.execute("""
                            INSERT OR REPLACE INTO vocabulary 
                            (vocab_date, word, word_type, phonetic, meaning, prefix, suffix, funny_story, other_forms, context_easy, context_medium, context_hard)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (item.get('date', datetime.now().strftime('%Y-%m-%d')), item['word'], item.get('word_type',''), item['phonetic'], item['meaning'], item.get('prefix',''), item.get('suffix',''), item['funny_story'], item.get('other_forms',''), item['context_easy'], item['context_medium'], item['context_hard']))
                    conn.commit(); conn.close()
                    st.success("Đã nạp thành công bộ từ vựng mới!"); st.rerun()
                except Exception as e: st.error(f"Lỗi JSON: {e}")