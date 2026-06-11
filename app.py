import streamlit as st
import sqlite3
import json
import re
from datetime import datetime

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
    .story-card { background-color: #FFFBEB; padding: 18px; border-radius: 12px; border: 1px dashed #F59E0B; font-style: italic; }
    .progress-text { font-size: 18px; font-weight: bold; color: #4F46E5; text-align: center; margin-bottom: 10px; }
    .score-box { padding: 25px; border-radius: 20px; text-align: center; margin-top: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border: 2px solid #E2E8F0; }
    .q-result { padding: 8px 12px; border-radius: 6px; margin-top: 8px; font-weight: bold; font-size: 14px; display: inline-block; }
</style>
""", unsafe_allow_html=True)

# Chạy khởi tạo database đầu luồng
init_db()

# --- CÁC HÀM XỬ LÝ NGỮ LIỆU BỔ TRỢ ---
def clean_and_bold_keyword(sentence, keyword):
    if not sentence: return ""
    clean_sentence = sentence.replace("**", "").replace("*", "")
    pattern = re.compile(re.escape(keyword), re.IGNORECASE)
    return pattern.sub(f"**{keyword}**", clean_sentence)

def hide_keyword_for_exercise(sentence, keyword):
    if not sentence: return ""
    clean_sentence = sentence.replace("**", "").replace("*", "")
    pattern = re.compile(re.escape(keyword), re.IGNORECASE)
    return pattern.sub("_______", clean_sentence)

# --- KHỞI TẠO BỘ NHỚ TRẠNG THÁI (SESSION STATE) ---
if "user" not in st.session_state: st.session_state.user = None
if "vocab_index" not in st.session_state: st.session_state.vocab_index = 0
if "current_date" not in st.session_state: st.session_state.current_date = ""

if "reading_submitted" not in st.session_state: st.session_state.reading_submitted = False
if "vocab_submitted" not in st.session_state: st.session_state.vocab_submitted = False
if "fill_blank_submitted" not in st.session_state: st.session_state.fill_blank_submitted = False

if "trigger_balloons" not in st.session_state: st.session_state.trigger_balloons = False
if "trigger_snow" not in st.session_state: st.session_state.trigger_snow = False

# Render hiệu ứng chúc mừng ngay đầu luồng nếu thỏa điều kiện
if st.session_state.trigger_balloons:
    st.balloons()
    st.session_state.trigger_balloons = False
if st.session_state.trigger_snow:
    st.snow()
    st.session_state.trigger_snow = False

# --- MÀN HÌNH ĐĂNG NHẬP (Nhấn Enter tự nhận Form) ---
if st.session_state.user is None:
    st.markdown("<div class='main-header'>🚀 English4Today - Hệ Thống Học Ngữ Liệu Gây Nghiện</div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.3, 1])
    with col2:
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Tài khoản:")
            password = st.text_input("Mật khẩu:", type="password")
            if st.form_submit_button("🔥 Tiến Vào Đấu Trường Học Tập", use_container_width=True):
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT username, role, allow_reading_part, allow_vocab_part 
                    FROM users WHERE LOWER(username)=LOWER(?) AND password=?
                """, (username.strip(), password.strip()))
                res = cursor.fetchone()
                conn.close()
                
                if res:
                    st.session_state.user = {
                        "username": res[0], "role": res[1], 
                        "allow_reading": int(res[2]), "allow_vocab": int(res[3])
                    }
                    st.rerun()
                else: 
                    st.error("❌ Sai tài khoản hoặc mật khẩu!")
    st.stop()

user = st.session_state.user

# --- SIDEBAR NAV ---
with st.sidebar:
    st.markdown(f"### 🎉 Chiến binh: **{user['username']}**")
    st.markdown("---")
    menu = []
    if user['allow_reading'] == 1 or user['role'] == 'admin': menu.append("📚 Thử Thách Bài Đọc")
    if user['allow_vocab'] == 1 or user['role'] == 'admin': menu.append("🧠 Từ Vựng Theo Ngày")
    if user['role'] == 'admin': menu.append("⚙️ Trung Tâm Admin")
    
    if not menu:
        st.warning("Tài khoản chưa được phân quyền. Hãy liên hệ bộ phận Admin.")
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
    cursor = conn.cursor()
    cursor.execute("SELECT id, level, title, content, grammar_points, quiz FROM reading_lessons")
    lessons = cursor.fetchall()
    conn.close()

    if not lessons: 
        st.info("Chưa có bài đọc nào trong cơ sở dữ liệu.")
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
                    if st.button("🔊 Đọc Toàn Bộ Bài Văn", use_container_width=True, key=f"read_btn_{l_id}"):
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
                                        st.markdown(f"<div class='q-result' style='background-color: #FEE2E2; color: #7F1D1D;'>❌ CHƯA ĐÚNG -> Đáp án: {q['answer']}</div>", unsafe_allow_html=True)
                        
                        st.markdown("---")
                        if not st.session_state.reading_submitted:
                            if st.button("🚀 Nộp Bài & Chấm Điểm Bài Đọc", use_container_width=True):
                                score_test = sum(1 for idx, q in enumerate(quizzes) if user_answers[idx] == q['answer'])
                                ratio_test = score_test / len(quizzes)
                                if score_test == len(quizzes): st.session_state.trigger_balloons = True
                                elif ratio_test >= 0.8: st.session_state.trigger_snow = True
                                
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
                            else:
                                bg_color, border_color, text_color = "#F8FAFC", "#94A3B8", "#1E293B"
                                comment = "👍 Khá tốt! Hãy nghiên cứu kỹ lại cấu trúc ngữ pháp để đạt điểm tuyệt đối nhé!"

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
                    except: st.write("Định dạng bộ câu hỏi trắc nghiệm của bài đọc bị lỗi cấu trúc dữ liệu.")

# --- PHẦN 2: TỪ VỰNG THEO NGÀY ---
elif choice == "🧠 Từ Vựng Theo Ngày":
    st.markdown("<div class='main-header'>🧠 Sổ Tay Từ Vựng Thông Minh Theo Ngày</div>", unsafe_allow_html=True)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT TRIM(vocab_date) FROM vocabulary ORDER BY vocab_date DESC")
    dates = [r[0] for r in cursor.fetchall()]
    conn.close()

    if not dates: 
        st.info("Chưa có từ vựng nào được nạp vào hệ thống.")
    else:
        selected_date = st.selectbox("📆 Chọn ngày học tập mục tiêu:", dates)
        
        if st.session_state.current_date != selected_date:
            st.session_state.vocab_index = 0
            st.session_state.current_date = selected_date
            st.session_state.vocab_submitted = False
            st.session_state.fill_blank_submitted = False
            
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT word, word_type, phonetic, meaning, prefix, suffix, funny_story, other_forms, context_easy, context_medium, context_hard FROM vocabulary WHERE TRIM(vocab_date)=?", (selected_date,))
        vocabs = cursor.fetchall()
        conn.close()
        
        total_words = len(vocabs)
        
        if total_words > 0:
            tab_learn, tab_game, tab_fill = st.tabs(["🌟 Chế Độ Học Thẻ Flashcard", "⚔️ Trận Chiến Trắc Nghiệm Nghĩa", "📝 Thử Thách Điền Từ Vào Câu"])
            
            with tab_learn:
                idx = st.session_state.vocab_index
                st.markdown(f"<div class='progress-text'>⚡ TIẾN ĐỘ: Từ {idx+1} / {total_words}</div>", unsafe_allow_html=True)
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
                    mm_text = f"🌟 Từ Khóa: {word} ({w_type})\n├── 🧬 Tiền tố: {prefix if prefix else 'N/A'}\n├── 🧬 Hậu tố: {suffix if suffix else 'N/A'}\n└── 🌿 Gia đình từ:\n"
                    if other_forms:
                        for line in other_forms.split('\n'): mm_text += f"    {line}\n"
                    st.code(mm_text, language="text")
                    
                with col_r:
                    st.markdown("#### 🧬 Các Loại Từ Liên Quan")
                    st.info(other_forms if other_forms else "Chưa bổ sung.")
                    
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
                        v_score_test = sum(1 for g_word, u_ans, g_correct in game_answers if u_ans == g_correct)
                        if v_score_test == total_words: st.session_state.trigger_balloons = True
                        elif (v_score_test / total_words) >= 0.8: st.session_state.trigger_snow = True
                        st.session_state.vocab_submitted = True
                        st.rerun()
                else:
                    v_score = sum(1 for g_word, u_ans, g_correct in game_answers if u_ans == g_correct)
                    st.markdown(f"<div class='score-box'><h3>📊 TỔNG KẾT ĐIỂM SỐ TỪ VỰNG</h3><p style='font-size: 28px; font-weight: 800; margin: 10px 0;'>Bạn thuộc: {v_score} / {total_words} Từ</p></div>", unsafe_allow_html=True)
                    if st.button("🔄 Khởi Động Lại Trận Chiến", use_container_width=True):
                        st.session_state.vocab_submitted = False
                        st.rerun()

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
                    if st.button("🚀 Kiểm Tra Đáp Án Điền Từ", use_container_width=True):
                        f_score_test = sum(1 for f_word, u_input in input_answers if u_input.lower() == f_word.lower())
                        if f_score_test == total_words: st.session_state.trigger_balloons = True
                        elif (f_score_test / total_words) >= 0.8: st.session_state.trigger_snow = True
                        st.session_state.fill_blank_submitted = True
                        st.rerun()
                else:
                    for f_word, u_input in input_answers:
                        if u_input.lower() == f_word.lower():
                            st.success(f"✅ Đúng: Từ **{f_word}**")
                        else:
                            st.error(f"❌ Chưa đúng -> Từ khóa chính xác: **{f_word}** (Bạn gõ: '{u_input}')")
                    if st.button("🔄 Làm Lại Thử Thách Điền Từ", use_container_width=True):
                        st.session_state.fill_blank_submitted = False
                        st.rerun()

# --- TRUNG TÂM ADMIN ---
elif choice == "⚙️ Trung Tâm Admin":
    st.title("⚙️ Trung Tâm Admin")
    t1, t2, t3, t4 = st.tabs(["👥 Thành Viên", "📂 Sửa/Xóa Bài", "📝 Nạp Bài Đọc Mới", "🧠 Nạp Từ Vựng Lớn"])
    
    with t1:
        st.subheader("👥 Quản Lý Thành Viên & Sao Lưu Dữ Liệu")
        
        # --- KHỐI SAO LƯU VÀ PHỤC HỒI DỮ LIỆU (GIẢI PHÁP CHO BẠN) ---
        with st.expander("💾 Trung Tâm Sao Lưu & Phục Hồi (Chống mất dữ liệu khi Update Code)", expanded=False):
            col_bk1, col_bk2 = st.columns(2)
            
            with col_bk1:
                st.markdown("##### 📥 Xuất Dữ Liệu (Backup)")
                if st.button("Tạo Bản Sao Lưu Hệ Thống 📦", use_container_width=True):
                    try:
                        conn = sqlite3.connect(DB_NAME)
                        cursor = conn.cursor()
                        
                        # Lấy dữ liệu toàn bộ các bảng
                        cursor.execute("SELECT username, password, role, allow_reading_part, allow_vocab_part FROM users")
                        users_data = [dict(zip(["username", "password", "role", "allow_reading_part", "allow_vocab_part"], r)) for r in cursor.fetchall()]
                        
                        cursor.execute("SELECT level, title, content, grammar_points, quiz FROM reading_lessons")
                        lessons_data = [dict(zip(["level", "title", "content", "grammar_points", "quiz"], r)) for r in cursor.fetchall()]
                        
                        cursor.execute("SELECT vocab_date, word, word_type, phonetic, meaning, prefix, suffix, funny_story, other_forms, context_easy, context_medium, context_hard FROM vocabulary")
                        vocab_data = [dict(zip(["vocab_date", "word", "word_type", "phonetic", "meaning", "prefix", "suffix", "funny_story", "other_forms", "context_easy", "context_medium", "context_hard"], r)) for r in cursor.fetchall()]
                        
                        conn.close()
                        
                        # Đóng gói thành 1 file JSON duy nhất
                        backup_payload = {
                            "users": users_data,
                            "reading_lessons": lessons_data,
                            "vocabulary": vocab_data
                        }
                        json_str = json.dumps(backup_payload, ensure_ascii=False, indent=4)
                        
                        # Tạo nút bấm Download trên Streamlit
                        st.download_button(
                            label="📥 Tải File Backup (.json) Về Máy",
                            data=json_str,
                            file_name=f"english4today_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json",
                            use_container_width=True
                        )
                        st.success("Tạo bản sao lưu thành công! Hãy bấm nút tải về phía trên.")
                    except Exception as e:
                        st.error(f"Lỗi sao lưu: {e}")
                        
            with col_bk2:
                st.markdown("##### 📤 Phục Hồi Dữ Liệu (Restore)")
                uploaded_backup_file = st.file_uploader("Chọn file backup (.json) đã lưu từ máy tính:", type=["json"], key="restore_uploader")
                
                if uploaded_backup_file is not None:
                    if st.button("🔥 Tiến Hành Khôi Phục Dữ Liệu", use_container_width=True, type="primary"):
                        try:
                            backup_data = json.load(uploaded_backup_file)
                            conn = sqlite3.connect(DB_NAME)
                            cursor = conn.cursor()
                            
                            # Khôi phục bảng Users (Bỏ qua nếu trùng username)
                            if "users" in backup_data:
                                for u in backup_data["users"]:
                                    cursor.execute("""
                                        INSERT OR IGNORE INTO users (username, password, role, allow_reading_part, allow_vocab_part)
                                        VALUES (?, ?, ?, ?, ?)
                                    """, (u["username"], u["password"], u["role"], u["allow_reading_part"], u["allow_vocab_part"]))
                            
                            # Khôi phục bảng Reading
                            if "reading_lessons" in backup_data:
                                # Xóa dữ liệu cũ để tránh trùng lặp đè lên nhau
                                cursor.execute("DELETE FROM reading_lessons")
                                for l in backup_data["reading_lessons"]:
                                    cursor.execute("""
                                        INSERT INTO reading_lessons (level, title, content, grammar_points, quiz)
                                        VALUES (?, ?, ?, ?, ?)
                                    """, (l["level"], l["title"], l["content"], l["grammar_points"], l["quiz"]))
                                    
                            # Khôi phục bảng Vocabulary
                            if "vocabulary" in backup_data:
                                cursor.execute("DELETE FROM vocabulary")
                                for v in backup_data["vocabulary"]:
                                    cursor.execute("""
                                        INSERT INTO vocabulary (vocab_date, word, word_type, phonetic, meaning, prefix, suffix, funny_story, other_forms, context_easy, context_medium, context_hard)
                                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                    """, (v["vocab_date"], v["word"], v["word_type"], v["phonetic"], v["meaning"], v["prefix"], v["suffix"], v["funny_story"], v["other_forms"], v["context_easy"], v["context_medium"], v["context_hard"]))
                            
                            conn.commit()
                            conn.close()
                            st.success("🎉 Hệ thống đã được khôi phục toàn vẹn dữ liệu từ file backup thành công!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Lỗi khôi phục: {e}")

        st.markdown("---")
        col_u1, col_u2 = st.columns([1.2, 2])
        
        # --- KHỐI THÊM HỌC VIÊN MỚI ---
        with col_u1:
            st.markdown("#### ➕ Thêm Học Viên Mới")
            with st.form("add_new_user_form", clear_on_submit=True):
                new_u = st.text_input("Tên tài khoản mới:").strip()
                new_p = st.text_input("Mật khẩu tài khoản:", type="password").strip()
                r_permission = st.checkbox("Quyền Học Phần 1 (Bài Đọc)", value=True)
                v_permission = st.checkbox("Quyền Học Phần 2 (Từ Vựng)", value=True)
                
                if st.form_submit_button("Lưu Học Viên 💾", use_container_width=True):
                    if not new_u or not new_p:
                        st.error("❌ Vui lòng nhập đầy đủ Tài khoản và Mật khẩu!")
                    else:
                        conn = sqlite3.connect(DB_NAME)
                        cursor = conn.cursor()
                        try:
                            cursor.execute("""
                                INSERT INTO users (username, password, role, allow_reading_part, allow_vocab_part) 
                                VALUES (?, ?, 'user', ?, ?)
                            """, (new_u, new_p, int(r_permission), int(v_permission)))
                            conn.commit()
                            st.success(f"🎉 Tạo tài khoản '{new_u}' thành công!")
                            st.rerun()
                        except sqlite3.IntegrityError:
                            st.error("❌ Tài khoản này đã tồn tại trên hệ thống!")
                        finally:
                            conn.close()

        # --- KHỐI DANH SÁCH & CẬP NHẬT/XÓA HỌC VIÊN ---
        with col_u2:
            st.markdown("#### 📋 Danh Sách Học Viên Hiện Có")
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, username, password, allow_reading_part, allow_vocab_part, role FROM users WHERE role != 'admin'")
            all_users = cursor.fetchall()
            conn.close()
            
            if not all_users:
                st.info("Chưa có học viên nào được tạo (ngoại trừ Admin mặc định).")
            else:
                for u_id, username, password, allow_r, allow_v, role in all_users:
                    with st.container(border=True):
                        st.markdown(f"👤 Học viên: **{username}** (MK: ` {password} `)")
                        col_chk1, col_chk2, col_btn_del = st.columns([1, 1, 1])
                        
                        with col_chk1:
                            active_r = st.checkbox("Quyền Bài Đọc", value=bool(allow_r), key=f"user_r_{u_id}")
                            if active_r != bool(allow_r):
                                conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
                                cursor.execute("UPDATE users SET allow_reading_part = ? WHERE user_id = ?", (int(active_r), u_id))
                                conn.commit(); conn.close()
                                st.rerun()
                                
                        with col_chk2:
                            active_v = st.checkbox("Quyền Từ Vựng", value=bool(allow_v), key=f"user_v_{u_id}")
                            if active_v != bool(allow_v):
                                conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
                                cursor.execute("UPDATE users SET allow_vocab_part = ? WHERE user_id = ?", (int(active_v), u_id))
                                conn.commit(); conn.close()
                                st.rerun()
                                
                        with col_btn_del:
                            if st.button("Xóa Học Viên 🗑️", key=f"del_user_{u_id}", use_container_width=True):
                                conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
                                cursor.execute("DELETE FROM users WHERE user_id = ?", (u_id,))
                                conn.commit(); conn.close()
                                st.success(f"🗑️ Đã xóa tài khoản {username}!")
                                st.rerun()
    with t2:
        st.subheader("🛠️ Trung Tâm Biên Tập & Chỉnh Sửa Ngữ Liệu")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.markdown("#### 📚 Quản lý Bài Đọc")
            conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
            cursor.execute("SELECT id, title, level, content FROM reading_lessons"); r_lessons = cursor.fetchall(); conn.close()
            for r_id, r_title, r_lvl, r_content in r_lessons:
                with st.container(border=True):
                    st.write(f"**[{r_lvl}] {r_title}**")
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        with st.popover("Sửa bài viết ✏️", use_container_width=True):
                            with st.form(f"edit_read_form_{r_id}"):
                                edit_title = st.text_input("Tiêu đề bài đọc:", value=r_title)
                                edit_lvl = st.text_input("Cấp độ (A1/B1/...):", value=r_lvl)
                                edit_content = st.text_area("Nội dung bài đọc:", value=r_content, height=150)
                                if st.form_submit_button("Cập nhật ngay 💾"):
                                    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
                                    cursor.execute("UPDATE reading_lessons SET title=?, level=?, content=? WHERE id=?", (edit_title, edit_lvl, edit_content, r_id))
                                    conn.commit(); conn.close(); st.success("Đã cập nhật!"); st.rerun()
                    with col_btn2:
                        if st.button("Xóa bài 🗑️", key=f"del_read_{r_id}", use_container_width=True):
                            conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
                            cursor.execute("DELETE FROM reading_lessons WHERE id=?", (r_id,))
                            conn.commit(); conn.close(); st.success("Đã xóa!"); st.rerun()
        with col_m2:
            st.markdown("#### 🧠 Quản lý Từ Vựng")
            conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
            cursor.execute("SELECT id, word, vocab_date, meaning, funny_story FROM vocabulary ORDER BY vocab_date DESC"); v_words = cursor.fetchall(); conn.close()
            for v_id, v_word, v_dt, v_meaning, v_story in v_words:
                with st.container(border=True):
                    st.write(f"📆 *{v_dt}* - **{v_word}** ({v_meaning})")
                    col_vbtn1, col_vbtn2 = st.columns(2)
                    with col_vbtn1:
                        with st.popover("Sửa từ này ✏️", use_container_width=True):
                            with st.form(f"edit_vocab_form_{v_id}"):
                                edit_word = st.text_input("Từ vựng:", value=v_word)
                                edit_meaning = st.text_input("Ý nghĩa:", value=v_meaning)
                                edit_story = st.text_area("Mẹo liên tưởng:", value=v_story, height=100)
                                if st.form_submit_button("Lưu thay đổi 💾"):
                                    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
                                    cursor.execute("UPDATE vocabulary SET word=?, meaning=?, funny_story=? WHERE id=?", (edit_word, edit_meaning, edit_story, v_id))
                                    conn.commit(); conn.close(); st.success("Đã cập nhật!"); st.rerun()
                    with col_vbtn2:
                        if st.button("Xóa từ 🗑️", key=f"del_voc_{v_id}", use_container_width=True):
                            conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
                            cursor.execute("DELETE FROM vocabulary WHERE id=?", (v_id,))
                            conn.commit(); conn.close(); st.success("Đã xóa!"); st.rerun()
    with t3:
        st.subheader("Nạp Bài Đọc Mới")
        js_r = st.text_area("Dán JSON bài đọc tại đây:", height=200)
        if st.button("Lưu bài đọc"):
            if js_r.strip():
                try:
                    d = json.loads(js_r.strip())
                    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
                    cursor.execute("INSERT INTO reading_lessons (level, title, content, grammar_points, quiz) VALUES (?,?,?,?,?)",
                                   (d.get("level","A1"), d.get("title",""), d.get("content",""), json.dumps(d.get("grammar_points",[])), json.dumps(d.get("quiz",[]))))
                    conn.commit(); conn.close(); st.success("Đã nạp bài đọc!"); st.rerun()
                except Exception as e: st.error(f"Lỗi JSON: {e}")
    with t4:
        st.subheader("Nạp Từ Vựng Lớn")
        js_v = st.text_area("Dán Mảng JSON từ vựng tại đây:", height=200)
        if st.button("Đóng gói nạp hàng loạt"):
            if js_v.strip():
                try:
                    v_list = json.loads(js_v.strip())
                    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
                    for item in v_list:
                        cursor.execute("""
                            INSERT OR REPLACE INTO vocabulary 
                            (vocab_date, word, word_type, phonetic, meaning, prefix, suffix, funny_story, other_forms, context_easy, context_medium, context_hard)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (item.get('date', datetime.now().strftime('%Y-%m-%d')), item['word'], item.get('word_type',''), item['phonetic'], item['meaning'], item.get('prefix',''), item.get('suffix',''), item['funny_story'], item.get('other_forms',''), item['context_easy'], item['context_medium'], item['context_hard']))
                    conn.commit(); conn.close(); st.success("Đã nạp bộ từ vựng mới!"); st.rerun()
                except Exception as e: st.error(f"Lỗi JSON: {e}")