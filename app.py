import streamlit as st
import json
import re
from datetime import datetime

# --- IMPORT TỪ CÁC LỚP ĐÃ TÁCH ---
from database import init_db, get_db_connection
from speech import execute_speech

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="English4Today - Học Gây Nghiện", page_icon="⚡", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
<script>
    // Hàm phát âm toàn cục viết bằng JS chuẩn, không bị chặn bởi iframe
    window.speakEnglishText = function(text) {
        if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel(); // Tắt giọng đọc cũ ngay lập tức
            let utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'en-US';
            utterance.rate = 0.85;
            window.speechSynthesis.speak(utterance);
        } else {
            alert("Trình duyệt của bạn không hỗ trợ phát âm!");
        }
    };
</script>
""", unsafe_allow_html=True)

# Chạy khởi tạo database trên đám mây đầu luồng
init_db()

# --- TỐI ƯU HÓA: BỘ LỌC CACHE DỮ LIỆU TỪ SUPABASE ---

@st.cache_data(ttl=600)  # Lưu dữ liệu trên bộ nhớ đệm trong 10 phút (600 giây)
def fetch_all_lessons():
    """Tải toàn bộ bài đọc và lưu vào bộ nhớ đệm"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, level, title, content, grammar_points, quiz FROM reading_lessons")
    lessons = cursor.fetchall()
    cursor.close()
    conn.close()
    return lessons

@st.cache_data(ttl=600)
def fetch_all_vocab_dates():
    """Tải danh sách ngày có từ vựng và lưu vào bộ nhớ đệm"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT TRIM(vocab_date) as vdate FROM vocabulary ORDER BY vdate DESC")
    dates = [r['vdate'] for r in cursor.fetchall()]
    cursor.close()
    conn.close()
    return dates

@st.cache_data(ttl=600)
def fetch_vocab_by_date(selected_date):
    """Tải từ vựng của một ngày cụ thể và lưu vào bộ nhớ đệm"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT word, word_type, phonetic, meaning, prefix, suffix, funny_story, other_forms, context_easy, context_medium, context_hard 
        FROM vocabulary WHERE TRIM(vocab_date)=%s
    """, (selected_date,))
    vocabs = cursor.fetchall()
    cursor.close()
    conn.close()
    return vocabs
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

if st.session_state.trigger_balloons:
    st.balloons(); st.session_state.trigger_balloons = False
if st.session_state.trigger_snow:
    st.snow(); st.session_state.trigger_snow = False

# --- MÀN HÌNH ĐĂNG NHẬP ---
if st.session_state.user is None:
    st.markdown("<div class='main-header'>🚀 English4Today - Hệ Thống Học Ngữ Liệu Gây Nghiện</div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.3, 1])
    with col2:
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Tài khoản:")
            password = st.text_input("Mật khẩu:", type="password")
            if st.form_submit_button("🔥 Tiến Vào Đấu Trường Học Tập", use_container_width=True):
                conn = get_db_connection(); cursor = conn.cursor()
                cursor.execute("""
                    SELECT username, role, allow_reading_part, allow_vocab_part 
                    FROM users WHERE LOWER(username)=LOWER(%s) AND password=%s
                """, (username.strip(), password.strip()))
                res = cursor.fetchone()
                cursor.close(); conn.close()
                
                if res:
                    st.session_state.user = {
                        "username": res['username'], "role": res['role'], 
                        "allow_reading": int(res['allow_reading_part']), "allow_vocab": int(res['allow_vocab_part'])
                    }
                    st.rerun()
                else: st.error("❌ Sai tài khoản hoặc mật khẩu!")
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
        st.warning("Tài khoản chưa được phân quyền.")
        choice = None
    else: choice = st.radio("Lộ trình hằng ngày:", menu)
        
    st.markdown("---")
    if st.button("Đăng xuất 🚪", use_container_width=True):
        st.session_state.user = None; st.rerun()

# --- PHẦN 1: THỬ THÁCH BÀI ĐỌC ---
if choice == "📚 Thử Thách Bài Đọc":
    st.markdown("<div class='main-header'>📚 Luyện Ngữ Liệu & Thử Thách Đọc Hiểu</div>", unsafe_allow_html=True)
    lessons = fetch_all_lessons()

    if not lessons: st.info("Chưa có bài đọc nào.")
    else:
        levels = sorted(list(set([r['level'] for r in lessons])))
        selected_lvl = st.segmented_control("Chọn cấp độ trình độ:", levels, default=levels[0])
        filtered = [l for l in lessons if l['level'] == selected_lvl]
        
        if filtered:
            titles = [l['title'] for l in filtered]
            sel_title = st.selectbox("Chọn bài viết mục tiêu:", titles)
            cur_lesson = [l for l in filtered if l['title'] == sel_title][0]
            
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1: st.markdown(f"### 📖 {cur_lesson['title']}")
                with col2:
                    execute_speech(content, label="🔊 Đọc Toàn Bộ Bài Văn")
                
                st.markdown(f"<div style='background-color: #F0FDF4; padding: 20px; border-radius: 12px; font-size: 18px; color: #1E293B; line-height: 1.7; border-left: 4px solid #10B981; margin-bottom: 15px;'>{cur_lesson['content']}</div>", unsafe_allow_html=True)
                
                with st.expander("💡 Xem Cấu Trúc Ngữ Pháp Chuyên Sâu"):
                    if cur_lesson['grammar_points']:
                        try:
                            g_data = json.loads(cur_lesson['grammar_points'])
                            for g in g_data:
                                st.warning(f"🔷 Cấu trúc: {g.get('structures')}")
                                st.write(f"👉 Giải thích: {g.get('explanation')}")
                        except: st.write(cur_lesson['grammar_points'])
                
                st.markdown("### 🎯 Đấu Trường Đọc Hiểu")
                if cur_lesson['quiz']:
                    try:
                        quizzes = json.loads(cur_lesson['quiz'])
                        user_answers = []
                        
                        for idx, q in enumerate(quizzes):
                            with st.container(border=True):
                                st.markdown(f"**Question {idx+1}: {q['question']}**")
                                ans = st.radio("Chọn câu trả lời:", q['options'], key=f"r_q_{cur_lesson['id']}_{idx}", disabled=st.session_state.reading_submitted)
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
                                if score_test == len(quizzes): st.session_state.trigger_balloons = True
                                elif (score_test / len(quizzes)) >= 0.8: st.session_state.trigger_snow = True
                                st.session_state.reading_submitted = True; st.rerun()
                        else:
                            score = sum(1 for idx, q in enumerate(quizzes) if user_answers[idx] == q['answer'])
                            st.markdown(f"<div class='score-box'><h3>🏆 KẾT QUẢ TỔNG KẾT ĐẤU TRƯỜNG</h3><p style='font-size: 28px; font-weight: 800; margin: 10px 0;'>Bạn đạt: {score} / {len(quizzes)} Câu đúng</p></div>", unsafe_allow_html=True)
                            if st.button("🔄 Làm Lại Bài Đọc Này", use_container_width=True):
                                st.session_state.reading_submitted = False; st.rerun()
                    except: st.write("Lỗi cấu trúc câu hỏi.")

# --- PHẦN 2: TỪ VỰNG THEO NGÀY ---
elif choice == "🧠 Từ Vựng Theo Ngày":
    st.markdown("<div class='main-header'>🧠 Sổ Tay Từ Vựng Thông Minh Theo Ngày</div>", unsafe_allow_html=True)
    dates = fetch_all_vocab_dates()

    if not dates: st.info("Chưa có từ vựng.")
    else:
        selected_date = st.selectbox("📆 Chọn ngày học tập mục tiêu:", dates)
        if st.session_state.current_date != selected_date:
            st.session_state.vocab_index = 0
            st.session_state.current_date = selected_date
            st.session_state.vocab_submitted = False
            st.session_state.fill_blank_submitted = False
            
       vocabs = fetch_vocab_by_date(selected_date)
        
        total_words = len(vocabs)
        if total_words > 0:
            tab_learn, tab_game, tab_fill = st.tabs(["🌟 Chế Độ Học Thẻ Flashcard", "⚔️ Trận Chiến Trắc Nghiệm Nghĩa", "📝 Thử Thách Điền Từ Vào Câu"])
            
            with tab_learn:
                idx = st.session_state.vocab_index
                st.markdown(f"<div class='progress-text'>⚡ TIẾN ĐỘ: Từ {idx+1} / {total_words}</div>", unsafe_allow_html=True)
                st.progress((idx + 1) / total_words)
                
                v = vocabs[idx]
                with st.container():
                    st.markdown(f"""
                    <div class='flashcard'>
                        <span style='font-size:36px; font-weight:bold; color:#4F46E5;'>{v['word']}</span> 
                        <span style='background-color:#EEF2F6; color:#64748B; font-size:14px; padding:4px 8px; border-radius:6px;'>{v['word_type'].upper()}</span>
                        <p style='font-size: 18px; margin-top:10px;'>🗣️ Phiên âm: <code>{v['phonetic']}</code> | <strong>Ý nghĩa: {v['meaning']}</strong></p>
                    </div>
                    """, unsafe_allow_html=True)
                    execute_speech(word, label="🔊 Phát Âm Từ Này")
                
                col_l, col_r = st.columns([1, 1])
                with col_l:
                    st.markdown(f"<div class='story-card'><strong>💡 Mẹo kể chuyện liên tưởng:</strong><br><br>{v['funny_story']}</div>", unsafe_allow_html=True)
                    st.markdown("#### 🗺️ Bản Đồ Cấu Trúc Từ")
                    mm_text = f"🌟 Từ Khóa: {v['word']} ({v['word_type']})\n├── 🧬 Tiền tố: {v['prefix'] if v['prefix'] else 'N/A'}\n├── 🧬 Hậu tố: {v['suffix'] if v['suffix'] else 'N/A'}\n└── 🌿 Gia đình từ:\n"
                    if v['other_forms']:
                        for line in v['other_forms'].split('\n'): mm_text += f"    {line}\n"
                    st.code(mm_text, language="text")
                with col_r:
                    st.markdown("#### 🧬 Các Loại Từ Liên Quan"); st.info(v['other_forms'] if v['other_forms'] else "Chưa bổ sung.")
                    st.markdown("#### 🎯 Ngữ Cảnh Ứng Dụng")
                    st.write("🟢 **Dễ:**", clean_and_bold_keyword(v['context_easy'], v['word']))
                    st.write("🔵 **Vừa:**", clean_and_bold_keyword(v['context_medium'], v['word']))
                    st.write("🔴 **Khó:**", clean_and_bold_keyword(v['context_hard'], v['word']))

                st.markdown("---")
                col_prev, _, col_next = st.columns([1, 2, 1])
                with col_prev:
                    if st.button("⬅️ Từ Trước Đó", use_container_width=True, disabled=(idx == 0)):
                        st.session_state.vocab_index -= 1; st.rerun()
                with col_next:
                    if st.button("Từ Tiếp Theo ➡️", use_container_width=True, disabled=(idx == total_words - 1)):
                        st.session_state.vocab_index += 1; st.rerun()

            with tab_game:
                st.markdown("### ⚔️ Thử Thách Trí Nhớ - Chọn Nghĩa Đúng Của Từ")
                game_answers = []
                for idx, v_item in enumerate(vocabs):
                    other_meanings = list(set([item['meaning'] for item in vocabs if item['meaning'] != v_item['meaning']]))[:3]
                    options = list(set([v_item['meaning']] + other_meanings)); options.sort()
                    
                    with st.container(border=True):
                        st.markdown(f"🎯 Từ số {idx+1}: **{v_item['word']}** nghĩa là gì?")
                        u_ans = st.radio(f"Chọn đáp án:", options, key=f"gm_v_{v_item['word']}", disabled=st.session_state.vocab_submitted)
                        game_answers.append((v_item['word'], u_ans, v_item['meaning']))
                        
                        if st.session_state.vocab_submitted:
                            if u_ans == v_item['meaning']: st.markdown("<div class='q-result' style='background-color: #DCFCE7; color: #14532D;'>🟢 CHÍNH XÁC!</div>", unsafe_allow_html=True)
                            else: st.markdown(f"<div class='q-result' style='background-color: #FEE2E2; color: #7F1D1D;'>❌ CHƯA ĐÚNG -> Nghĩa chuẩn là: {v_item['meaning']}</div>", unsafe_allow_html=True)
                
                st.markdown("---")
                if not st.session_state.vocab_submitted:
                    if st.button("🚀 Nộp Bài Khảo Sát Từ Vựng", use_container_width=True):
                        v_score_test = sum(1 for w, u, g in game_answers if u == g)
                        if v_score_test == total_words: st.session_state.trigger_balloons = True
                        elif (v_score_test / total_words) >= 0.8: st.session_state.trigger_snow = True
                        st.session_state.vocab_submitted = True; st.rerun()
                else:
                    v_score = sum(1 for w, u, g in game_answers if u == g)
                    st.markdown(f"<div class='score-box'><h3>📊 TỔNG KẾT ĐIỂM SỐ TỪ VỰNG</h3><p style='font-size: 28px; font-weight: 800; margin: 10px 0;'>Bạn thuộc: {v_score} / {total_words} Từ</p></div>", unsafe_allow_html=True)
                    if st.button("🔄 Khởi Động Lại Trận Chiến", use_container_width=True): st.session_state.vocab_submitted = False; st.rerun()

            with tab_fill:
                st.markdown("### 📝 Thử Thách Tư Duy - Điền Từ Thích Hợp Vào Chỗ Trống")
                input_answers = []
                for idx, v_item in enumerate(vocabs):
                    hidden_sentence = hide_keyword_for_exercise(v_item['context_easy'], v_item['word'])
                    with st.container(border=True):
                        st.markdown(f"**Câu hỏi {idx+1}:** {hidden_sentence}")
                        user_input = st.text_input("Nhập từ tiếng Anh còn thiếu:", key=f"fill_{v_item['word']}", disabled=st.session_state.fill_blank_submitted)
                        input_answers.append((v_item['word'], user_input.strip()))
                
                st.markdown("---")
                if not st.session_state.fill_blank_submitted:
                    if st.button("🚀 Kiểm Tra Đáp Án Điền Từ", use_container_width=True):
                        f_score_test = sum(1 for w, u in input_answers if u.lower() == w.lower())
                        if f_score_test == total_words: st.session_state.trigger_balloons = True
                        elif (f_score_test / total_words) >= 0.8: st.session_state.trigger_snow = True
                        st.session_state.fill_blank_submitted = True; st.rerun()
                else:
                    for w, u in input_answers:
                        if u.lower() == w.lower(): st.success(f"✅ Đúng: Từ **{w}**")
                        else: st.error(f"❌ Chưa đúng -> Từ khóa chính xác: **{w}** (Bạn gõ: '{u}')")
                    if st.button("🔄 Làm Lại Thử Thách Điền Từ", use_container_width=True): st.session_state.fill_blank_submitted = False; st.rerun()

# --- TRUNG TÂM ADMIN ---
elif choice == "⚙️ Trung Tâm Admin":
    st.title("⚙️ Trung Tâm Admin")
    t1, t2, t3, t4 = st.tabs(["👥 Thành Viên", "📂 Sửa/Xóa Bài", "📝 Nạp Bài Đọc Mới", "🧠 Nạp Từ Vựng Lớn"])
    
    with t1:
        st.subheader("👥 Quản Lý Thành Viên Hệ Thống")
        col_u1, col_u2 = st.columns([1.2, 2])
        
        with col_u1:
            st.markdown("#### ➕ Thêm Học Viên Mới")
            with st.form("add_new_user_form", clear_on_submit=True):
                new_u = st.text_input("Tên tài khoản mới:").strip()
                new_p = st.text_input("Mật khẩu tài khoản:", type="password").strip()
                r_permission = st.checkbox("Quyền Học Phần 1 (Bài Đọc)", value=True)
                v_permission = st.checkbox("Quyền Học Phần 2 (Từ Vựng)", value=True)
                
                if st.form_submit_button("Lưu Học Viên 💾", use_container_width=True):
                    if not new_u or not new_p: st.error("❌ Vui lòng nhập đầy đủ!")
                    else:
                        conn = get_db_connection(); cursor = conn.cursor()
                        try:
                            cursor.execute("""
                                INSERT INTO users (username, password, role, allow_reading_part, allow_vocab_part) 
                                VALUES (%s, %s, 'user', %s, %s)
                            """, (new_u, new_p, int(r_permission), int(v_permission)))
                            conn.commit()
                            st.cache_data.clear()
                            st.success(f"🎉 Tạo tài khoản '{new_u}' thành công!")
                            st.rerun()
                        except: st.error("❌ Tài khoản này đã tồn tại trên hệ thống!")
                        finally: cursor.close(); conn.close()

        with col_u2:
            st.markdown("#### 📋 Danh Sách Học Viên Hiện Có")
            conn = get_db_connection(); cursor = conn.cursor()
            cursor.execute("SELECT user_id, username, password, allow_reading_part, allow_vocab_part FROM users WHERE role != 'admin'")
            all_users = cursor.fetchall()
            cursor.close(); conn.close()
            
            if not all_users: st.info("Chưa có học viên nào.")
            else:
                for u in all_users:
                    with st.container(border=True):
                        st.markdown(f"👤 Học viên: **{u['username']}** (MK: ` {u['password']} `)")
                        col_chk1, col_chk2, col_btn_del = st.columns([1, 1, 1])
                        
                        with col_chk1:
                            active_r = st.checkbox("Quyền Bài Đọc", value=bool(u['allow_reading_part']), key=f"user_r_{u['user_id']}")
                            if active_r != bool(u['allow_reading_part']):
                                conn = get_db_connection(); cursor = conn.cursor()
                                cursor.execute("UPDATE users SET allow_reading_part = %s WHERE user_id = %s", (int(active_r), u['user_id']))
                                conn.commit(); cursor.close(); conn.close(); st.cache_data.clear(); st.rerun()
                                
                        with col_chk2:
                            active_v = st.checkbox("Quyền Từ Vựng", value=bool(u['allow_vocab_part']), key=f"user_v_{u['user_id']}")
                            if active_v != bool(u['allow_vocab_part']):
                                conn = get_db_connection(); cursor = conn.cursor()
                                cursor.execute("UPDATE users SET allow_vocab_part = %s WHERE user_id = %s", (int(active_v), u['user_id']))
                                conn.commit(); cursor.close(); conn.close(); st.cache_data.clear(); st.rerun()
                                
                        with col_btn_del:
                            if st.button("Xóa Học Viên 🗑️", key=f"del_user_{u['user_id']}", use_container_width=True):
                                conn = get_db_connection(); cursor = conn.cursor()
                                cursor.execute("DELETE FROM users WHERE user_id = %s", (u['user_id'],))
                                conn.commit(); cursor.close(); conn.close(); st.cache_data.clear(); st.success("Đã xóa!"); st.rerun()
    with t2:
        st.subheader("🛠️ Trung Tâm Biên Tập & Chỉnh Sửa Ngữ Liệu")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.markdown("#### 📚 Quản lý Bài Đọc")
            conn = get_db_connection(); cursor = conn.cursor()
            cursor.execute("SELECT id, title, level, content FROM reading_lessons"); r_lessons = cursor.fetchall(); cursor.close(); conn.close()
            for r in r_lessons:
                with st.container(border=True):
                    st.write(f"**[{r['level']}] {r['title']}**")
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        with st.popover("Sửa bài viết ✏️", use_container_width=True):
                            with st.form(f"edit_read_form_{r['id']}"):
                                edit_title = st.text_input("Tiêu đề bài đọc:", value=r['title'])
                                edit_lvl = st.text_input("Cấp độ (A1/B1/...):", value=r['level'])
                                edit_content = st.text_area("Nội dung bài đọc:", value=r['content'], height=150)
                                if st.form_submit_button("Cập nhật ngay 💾"):
                                    conn = get_db_connection(); cursor = conn.cursor()
                                    cursor.execute("UPDATE reading_lessons SET title=%s, level=%s, content=%s WHERE id=%s", (edit_title, edit_lvl, edit_content, r['id']))
                                    conn.commit(); cursor.close(); conn.close(); st.cache_data.clear(); st.success("Đã cập nhật!"); st.rerun()
                    with col_btn2:
                        if st.button("Xóa bài 🗑️", key=f"del_read_{r['id']}", use_container_width=True):
                            conn = get_db_connection(); cursor = conn.cursor()
                            cursor.execute("DELETE FROM reading_lessons WHERE id=%s", (r['id'],))
                            conn.commit(); cursor.close(); conn.close(); st.cache_data.clear(); st.success("Đã xóa!"); st.rerun()
        with col_m2:
            st.markdown("#### 🧠 Quản lý Từ Vựng")
            conn = get_db_connection(); cursor = conn.cursor()
            cursor.execute("SELECT id, word, vocab_date, meaning, funny_story FROM vocabulary ORDER BY vocab_date DESC"); v_words = cursor.fetchall(); cursor.close(); conn.close()
            for v in v_words:
                with st.container(border=True):
                    st.write(f"📆 *{v['vocab_date']}* - **{v['word']}** ({v['meaning']})")
                    col_vbtn1, col_vbtn2 = st.columns(2)
                    with col_vbtn1:
                        with st.popover("Sửa từ này ✏️", use_container_width=True):
                            with st.form(f"edit_vocab_form_{v['id']}"):
                                edit_word = st.text_input("Từ vựng:", value=v['word'])
                                edit_meaning = st.text_input("Ý nghĩa:", value=v['meaning'])
                                edit_story = st.text_area("Mẹo liên tưởng:", value=v['funny_story'], height=100)
                                if st.form_submit_button("Lưu thay đổi 💾"):
                                    conn = get_db_connection(); cursor = conn.cursor()
                                    cursor.execute("UPDATE vocabulary SET word=%s, meaning=%s, funny_story=%s WHERE id=%s", (edit_word, edit_meaning, edit_story, v['id']))
                                    conn.commit(); cursor.close(); conn.close();st.cache_data.clear(); st.success("Đã cập nhật!"); st.rerun()
                    with col_vbtn2:
                        if st.button("Xóa từ 🗑️", key=f"del_voc_{v['id']}", use_container_width=True):
                            conn = get_db_connection(); cursor = conn.cursor()
                            cursor.execute("DELETE FROM vocabulary WHERE id=%s", (v['id'],))
                            conn.commit(); cursor.close(); conn.close();st.cache_data.clear(); st.success("Đã xóa!"); st.rerun()
    with t3:
        st.subheader("Nạp Bài Đọc Mới")
        js_r = st.text_area("Dán JSON bài đọc tại đây:", height=200)
        if st.button("Lưu bài đọc"):
            if js_r.strip():
                try:
                    d = json.loads(js_r.strip())
                    conn = get_db_connection(); cursor = conn.cursor()
                    cursor.execute("INSERT INTO reading_lessons (level, title, content, grammar_points, quiz) VALUES (%s,%s,%s,%s,%s)",
                                   (d.get("level","A1"), d.get("title",""), d.get("content",""), json.dumps(d.get("grammar_points",[]), ensure_ascii=False), json.dumps(d.get("quiz",[]), ensure_ascii=False)))
                    conn.commit(); cursor.close(); conn.close(); st.cache_data.clear(); st.success("Đã nạp bài đọc!"); st.rerun()
                except Exception as e: st.error(f"Lỗi JSON: {e}")
    with t4:
        st.subheader("Nạp Từ Vựng Lớn")
        js_v = st.text_area("Dán Mảng JSON từ vựng tại đây:", height=200)
        if st.button("Đóng gói nạp hàng loạt"):
            if js_v.strip():
                try:
                    v_list = json.loads(js_v.strip())
                    conn = get_db_connection(); cursor = conn.cursor()
                    for item in v_list:
                        cursor.execute("""
                            INSERT INTO vocabulary 
                            (vocab_date, word, word_type, phonetic, meaning, prefix, suffix, funny_story, other_forms, context_easy, context_medium, context_hard)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (word) DO UPDATE SET
                                vocab_date = EXCLUDED.vocab_date,
                                word_type = EXCLUDED.word_type,
                                phonetic = EXCLUDED.phonetic,
                                meaning = EXCLUDED.meaning,
                                prefix = EXCLUDED.prefix,
                                suffix = EXCLUDED.suffix,
                                funny_story = EXCLUDED.funny_story,
                                other_forms = EXCLUDED.other_forms,
                                context_easy = EXCLUDED.context_easy,
                                context_medium = EXCLUDED.context_medium,
                                context_hard = EXCLUDED.context_hard
                        """, (item.get('date', datetime.now().strftime('%Y-%m-%d')), item['word'], item.get('word_type',''), item['phonetic'], item['meaning'], item.get('prefix',''), item.get('suffix',''), item['funny_story'], item.get('other_forms',''), item['context_easy'], item['context_medium'], item['context_hard']))
                    conn.commit(); cursor.close(); conn.close(); st.cache_data.clear(); st.success("Đã nạp bộ từ vựng mới!"); st.rerun()
                except Exception as e: st.error(f"Lỗi JSON: {e}")
