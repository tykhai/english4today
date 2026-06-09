import streamlit as st
import sqlite3
import json
import re
from datetime import datetime
import database
import auth

# Khởi tạo DB
database.init_db()

st.set_page_config(page_title="English4Today - Học Gây Nghiện", page_icon="⚡", layout="wide")

# --- HIỆU ỨNG PHÁO HOA AN TOÀN (KHÔNG BỊ NUỐT KHI RERUN) ---
if "trigger_balloons" in st.session_state and st.session_state.trigger_balloons:
    st.balloons()
    st.session_state.trigger_balloons = False  # Reset ngay sau khi nổ

if "trigger_snow" in st.session_state and st.session_state.trigger_snow:
    st.snow()
    st.session_state.trigger_snow = False

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

# --- HÀM PHÁT ÂM ---
def execute_speech(text_to_speak):
    clean_text = text_to_speak.replace("'", "\\'").replace("\n", " ").replace("**", "")
    js_code = f"""
    <iframe srcdoc="<script>window.speechSynthesis.cancel(); let u = new SpeechSynthesisUtterance('{clean_text}'); u.lang = 'en-US'; u.rate = 0.85; window.speechSynthesis.speak(u);</script>" style="display:none; width:0; height:0; border:none;"></iframe>
    """
    st.html(js_code)

# --- HÀM XỬ LÝ IN ĐẬM TỪ KHÓA CHUẨN XÁC ---
def clean_and_bold_keyword(sentence, keyword):
    if not sentence: return ""
    # Loại bỏ hết tất cả các ký tự sao cũ có sẵn trong chuỗi tránh lỗi render lặp dấu
    clean_sentence = sentence.replace("**", "").replace("*", "")
    # Thực hiện tìm và thay thế từ khóa (không phân biệt hoa thường) bằng định dạng Markdown sạch
    pattern = re.compile(f"({re.escape(keyword)})", re.IGNORECASE)
    return pattern.sub(r"**\1**", clean_sentence)

def hide_keyword_for_exercise(sentence, keyword):
    if not sentence: return ""
    clean_sentence = sentence.replace("**", "").replace("*", "")
    pattern = re.compile(re.escape(keyword), re.IGNORECASE)
    return pattern.sub("_______", clean_sentence)

# Khởi tạo trạng thái ứng dụng
if "user" not in st.session_state: st.session_state.user = None
if "vocab_index" not in st.session_state: st.session_state.vocab_index = 0
if "current_date" not in st.session_state: st.session_state.current_date = ""
if "reading_submitted" not in st.session_state: st.session_state.reading_submitted = False
if "vocab_submitted" not in st.session_state: st.session_state.vocab_submitted = False
if "fill_blank_submitted" not in st.session_state: st.session_state.fill_blank_submitted = False

# --- MÀN HÌNH ĐĂNG NHẬP (NHẬP MẬT KHẨU RỒI ENTER SẼ TỰ ĐĂNG NHẬP) ---
if st.session_state.user is None:
    st.markdown("<div class='main-header'>🚀 English4Today - Hệ Thống Học Ngữ Liệu Gây Nghiện</div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.3, 1])
    with col2:
        # Sử dụng st.form để tận dụng tính năng nhấn phím Enter trên bàn phím tự submit form
        with st.form("login_form", clear_on_submit=False):
            username_input = st.text_input("Tài khoản:")
            password_input = st.text_input("Mật khẩu:", type="password")
            submit_login = st.form_submit_button("🔥 Tiến Vào Đấu Trường Học Tập", use_container_width=True)
            
            if submit_login:
                user_info = auth.verify_user(username_input, password_input)
                if user_info:
                    st.session_state.user = user_info
                    st.rerun()
                else:
                    st.error("❌ Tài khoản hoặc mật khẩu không chính xác!")
    st.stop()

user = st.session_state.user

# --- SIDEBAR DI CHUYỂN ---
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

# --- PHẦN 1: BÀI ĐỌC ---
if choice == "📚 Thử Thách Bài Đọc":
    st.markdown("<div class='main-header'>📚 Luyện Ngữ Liệu & Thử Thách Đọc Hiểu</div>", unsafe_allow_html=True)
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, level, title, content, grammar_points, quiz FROM reading_lessons")
    lessons = cursor.fetchall()
    conn.close()

    if not lessons: st.info("Chưa có bài đọc nào.")
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
                                bg, bc, tc = "#ECFDF5", "#10B981", "#064E3B"
                                comment = "🔥 Tuyệt đỉnh thiên tài! Bạn đã thấu hiểu hoàn toàn 100% ngữ cảnh bài đọc này!"
                            elif ratio >= 0.8:
                                bg, bc, tc = "#EFF6FF", "#3B82F6", "#1E3A8A"
                                comment = "🌟 Xuất sắc! Bộ não của bạn bắt nhịp ngữ liệu rất nhanh, giữ vững phong độ nhé!"
                            elif ratio < 0.5:
                                bg, bc, tc = "#FFF7ED", "#F97316", "#7C2D12"
                                comment = "💪 Đừng nản lòng nhé! Bấm 'Làm lại' để đọc kỹ và chinh phục lại câu hỏi nào!"
                            else:
                                bg, bc, tc = "#F8FAFC", "#94A3B8", "#1E293B"
                                comment = "👍 Khá tốt! Bạn đã vượt qua mức trung bình. Hãy cố gắng đạt điểm tối đa ở lần tới!"

                            st.markdown(f"<div class='score-box' style='background: {bg}; border: 2px solid {bc}; color: {tc};'><h3>🏆 KẾT QUẢ TỔNG KẾT ĐẤU TRƯỜNG</h3><p style='font-size: 28px; font-weight: 800; margin: 10px 0;'>Bạn đạt: {score} / {total_q} Câu đúng</p><p style='font-size: 16px; font-weight: 600;'>💡 Lời khuyên: {comment}</p></div>", unsafe_allow_html=True)
                            if st.button("🔄 Làm Lại Bài Đọc Này", use_container_width=True):
                                st.session_state.reading_submitted = False
                                st.rerun()
                    except Exception as e: st.write("Chưa có câu hỏi.")

# --- PHẦN 2: TỪ VỰNG NGÀY ---
elif choice == "🧠 Từ Vựng Theo Ngày":
    st.markdown("<div class='main-header'>🧠 Sổ Tay Từ Vựng Thông Minh Theo Ngày</div>", unsafe_allow_html=True)
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT TRIM(vocab_date) FROM vocabulary ORDER BY vocab_date DESC")
    dates = [r[0] for r in cursor.fetchall()]
    conn.close()

    if not dates: st.info("Chưa có dữ liệu từ vựng.")
    else:
        selected_date = st.selectbox("📆 Chọn ngày học tập mục tiêu:", dates)
        if st.session_state.current_date != selected_date:
            st.session_state.vocab_index = 0
            st.session_state.current_date = selected_date
            st.session_state.vocab_submitted = False
            st.session_state.fill_blank_submitted = False
            
        conn = database.get_connection()
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
                st.markdown(f"<div class='flashcard'><span style='font-size:36px; font-weight:bold; color:#4F46E5;'>{word}</span> <span style='background-color:#EEF2F6; color:#64748B; font-size:14px; padding:4px 8px; border-radius:6px;'>{w_type.upper()}</span><p style='font-size: 18px; margin-top:10px;'>🗣️ Phiên âm: <code>{phonetic}</code> | <strong>Ý nghĩa: {meaning}</strong></p></div>", unsafe_allow_html=True)
                
                if st.button("🔊 Phát Âm Từ Này", key=f"spk_{word}"): execute_speech(word)
                
                col_l, col_r = st.columns([1, 1])
                with col_l:
                    st.markdown(f"<div class='story-card'><strong>💡 Mẹo kể chuyện liên tưởng:</strong><br><br>{story}</div>", unsafe_allow_html=True)
                    st.markdown("#### 🗺️ Bản Đồ Cấu Trúc Từ")
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
                col_prev, _, col_next = st.columns([1, 2, 1])
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
                                st.markdown(f"<div class='q-result' style='background-color: #FEE2E2; color: #7F1D1D;'>❌ CHƯA ĐÚNG -> Đáp án: {g_correct_meaning}</div>", unsafe_allow_html=True)
                
                st.markdown("---")
                if not st.session_state.vocab_submitted:
                    if st.button("🚀 Nộp Bài Khảo Sát Từ Vựng", use_container_width=True):
                        v_score_test = sum(1 for g_word, u_ans, g_correct in game_answers if u_ans == g_correct)
                        v_ratio_test = v_score_test / total_words
                        if v_score_test == total_words: st.session_state.trigger_balloons = True
                        elif v_ratio_test >= 0.8: st.session_state.trigger_snow = True
                        st.session_state.vocab_submitted = True
                        st.rerun()
                else:
                    v_score = sum(1 for g_word, u_ans, g_correct in game_answers if u_ans == g_correct)
                    v_ratio = v_score / total_words
                    if v_score == total_words:
                        bg, bc, tc = "#ECFDF5", "#10B981", "#064E3B"
                        b_comment = "🏆 Bộ não bách phát bách trúng! Bạn đã thuộc làu không sót một từ nào hôm nay!"
                    elif v_ratio >= 0.8:
                        bg, bc, tc = "#EFF6FF", "#3B82F6", "#1E3A8A"
                        b_comment = "🌟 Quá xuất sắc! Bạn nhớ được hầu hết lượng từ vựng nâng cao rồi đó!"
                    elif v_ratio < 0.5:
                        bg, bc, tc = "#FFF7ED", "#F97316", "#7C2D12"
                        b_comment = "💪 Lật lại thẻ Flashcard lướt qua mẹo liên tưởng một lần nữa để găm từ vào đầu nhé!"
                    else:
                        bg, bc, tc = "#F8FAFC", "#94A3B8", "#1E293B"
                        b_comment = "👍 Bạn đã đi được nửa chặng đường thành công rồi. Làm lại để đạt điểm tối đa!"

                    st.markdown(f"<div class='score-box' style='background: {bg}; border: 2px solid {bc}; color: {tc};'><h3>📊 TỔNG KẾT ĐIỂM SỐ TỪ VỰNG</h3><p style='font-size: 28px; font-weight: 800; margin: 10px 0;'>Bạn thuộc: {v_score} / {total_words} Từ</p><p style='font-size: 16px; font-weight: 600;'>💡 Nhận xét: {b_comment}</p></div>", unsafe_allow_html=True)
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
                        f_ratio_test = f_score_test / total_words
                        if f_score_test == total_words: st.session_state.trigger_balloons = True
                        elif f_ratio_test >= 0.8: st.session_state.trigger_snow = True
                        st.session_state.fill_blank_submitted = True
                        st.rerun()
                else:
                    f_score = 0
                    for f_word, u_input in input_answers:
                        if u_input.lower() == f_word.lower():
                            st.success(f"✅ Đúng: Từ **{f_word}**")
                            f_score += 1
                        else:
                            st.error(f"❌ Chưa đúng -> Từ chuẩn: **{f_word}** (Bạn gõ: '{u_input}')")
                    
                    f_ratio = f_score / total_words
                    if f_score == total_words:
                        bg, bc, tc = "#ECFDF5", "#10B981", "#064E3B"
                        f_comment = "🏅 Vô địch điền từ! Khả năng nhớ ngữ cảnh chính xác của bạn quá đỉnh cao!"
                    elif f_ratio >= 0.8:
                        bg, bc, tc = "#EFF6FF", "#3B82F6", "#1E3A8A"
                        f_comment = "🌟 Tuyệt vời! Bạn chỉ mắc vài lỗi nhỏ thôi, tổng quan rất tốt!"
                    else:
                        bg, bc, tc = "#F8FAFC", "#94A3B8", "#1E293B"
                        f_comment = "💪 Thử sức lại lần nữa để ghi nhớ sâu sắc 100% ngữ cảnh từ vựng nhé!"

                    st.markdown(f"<div class='score-box' style='background: {bg}; border: 2px solid {bc}; color: {tc};'><h3>📊 KẾT QUẢ ĐIỀN TỪ NGỮ CẢNH</h3><p style='font-size: 28px; font-weight: 800; margin: 10px 0;'>Chính xác: {f_score} / {total_words} Câu</p><p style='font-size: 16px; font-weight: 600;'>💡 Lời khuyên: {f_comment}</p></div>", unsafe_allow_html=True)
                    if st.button("🔄 Làm Lại Thử Thách Điền Từ", use_container_width=True):
                        st.session_state.fill_blank_submitted = False
                        st.rerun()

# --- TRUNG TÂM ADMIN ---
elif choice == "⚙️ Trung Tâm Admin":
    st.title("⚙️ Trung Tâm Quản Trị Hệ Thống Admin")
    t1, t2, t3, t4 = st.tabs(["👥 Quản Lý Thành Viên", "🛠️ Quản Lý Ngữ Liệu", "📝 Nạp Bài Đọc", "🧠 Nạp Từ Vựng"])
    
    with t1:
        st.subheader("➕ Thêm Thành Viên Mới")
        with st.form("add_user_form"):
            new_u = st.text_input("Tên tài khoản học viên:")
            new_p = st.text_input("Mật khẩu truy cập:")
            r_part = st.checkbox("Quyền học Phần 1 (Bài Đọc)", value=True)
            v_part = st.checkbox("Quyền học Phần 2 (Từ Vựng)", value=True)
            if st.form_submit_button("Lưu Học Viên Khóa Học"):
                if new_u and new_p:
                    if auth.add_new_user(new_u, new_p, r_part, v_part):
                        st.success("🎉 Đã thêm học viên mới thành công!")
                        st.rerun()
                    else: st.error("❌ Tên tài khoản đã tồn tại trên hệ thống!")
        
        st.markdown("---")
        st.subheader("📋 Danh Sách Thành Viên Hiện Tại")
        all_users = auth.get_all_users()
        if not all_users:
            st.info("Chưa có học viên nào được đăng ký.")
        else:
            for uid, uname, upass, urole, ur_p, uv_p in all_users:
                with st.container(border=True):
                    col_u1, col_u2, col_u3, col_u4 = st.columns([1.5, 2, 1.2, 1])
                    with col_u1:
                        st.markdown(f"👤 Học viên: **{uname}**")
                        st.caption(f"Mật khẩu: `{upass}`")
                    with col_u2:
                        chk_r = st.checkbox("Quyền bài đọc (P1)", value=bool(ur_p), key=f"chk_r_{uid}")
                        chk_v = st.checkbox("Quyền từ vựng (P2)", value=bool(uv_p), key=f"chk_v_{uid}")
                    with col_u3:
                        if st.button("Cập nhật 💾", key=f"btn_up_{uid}", use_container_width=True):
                            auth.update_user_permissions(uid, chk_r, chk_v)
                            st.success(f"Đã lưu quyền cho {uname}")
                            st.rerun()
                    with col_u4:
                        if st.button("Xóa 🗑️", key=f"btn_del_u_{uid}", use_container_width=True):
                            auth.delete_user(uid)
                            st.warning(f"Đã xóa tài khoản {uname}")
                            st.rerun()

    with t2:
        st.subheader("🛠️ Biên Tập Ngữ Liệu Thô")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.markdown("#### 📚 Bài Đọc")
            conn = database.get_connection(); cursor = conn.cursor()
            cursor.execute("SELECT id, title, level, content FROM reading_lessons"); r_lessons = cursor.fetchall(); conn.close()
            for r_id, r_title, r_lvl, r_content in r_lessons:
                with st.container(border=True):
                    st.write(f"**[{r_lvl}] {r_title}**")
                    col_b1, col_b2 = st.columns(2)
                    with col_b1:
                        with st.popover("Sửa bài ✏️", use_container_width=True):
                            with st.form(f"edit_r_form_{r_id}"):
                                e_title = st.text_input("Tiêu đề bài đọc:", value=r_title)
                                e_lvl = st.text_input("Cấp độ:", value=r_lvl)
                                e_content = st.text_area("Nội dung:", value=r_content, height=150)
                                if st.form_submit_button("Lưu 💾"):
                                    conn = database.get_connection(); cursor = conn.cursor()
                                    cursor.execute("UPDATE reading_lessons SET title=?, level=?, content=? WHERE id=?", (e_title, e_lvl, e_content, r_id))
                                    conn.commit(); conn.close(); st.success("Xong!"); st.rerun()
                    with col_b2:
                        if st.button("Xóa 🗑️", key=f"del_read_{r_id}", use_container_width=True):
                            conn = database.get_connection(); cursor = conn.cursor()
                            cursor.execute("DELETE FROM reading_lessons WHERE id=?", (r_id,))
                            conn.commit(); conn.close(); st.rerun()
        with col_m2:
            st.markdown("#### 🧠 Từ Vựng")
            conn = database.get_connection(); cursor = conn.cursor()
            cursor.execute("SELECT id, word, vocab_date, meaning, funny_story FROM vocabulary ORDER BY vocab_date DESC"); v_words = cursor.fetchall(); conn.close()
            for v_id, v_word, v_dt, v_meaning, v_story in v_words:
                with st.container(border=True):
                    st.write(f"📆 *{v_dt}* - **{v_word}** ({v_meaning})")
                    col_vb1, col_vb2 = st.columns(2)
                    with col_vb1:
                        with st.popover("Sửa từ ✏️", use_container_width=True):
                            with st.form(f"edit_v_form_{v_id}"):
                                e_word = st.text_input("Từ vựng:", value=v_word)
                                e_meaning = st.text_input("Ý nghĩa:", value=v_meaning)
                                e_story = st.text_area("Mẹo liên tưởng:", value=v_story, height=100)
                                if st.form_submit_button("Lưu 💾"):
                                    conn = database.get_connection(); cursor = conn.cursor()
                                    cursor.execute("UPDATE vocabulary SET word=?, meaning=?, funny_story=? WHERE id=?", (e_word, e_meaning, e_story, v_id))
                                    conn.commit(); conn.close(); st.success("Xong!"); st.rerun()
                    with col_vb2:
                        if st.button("Xóa 🗑️", key=f"del_voc_{v_id}", use_container_width=True):
                            conn = database.get_connection(); cursor = conn.cursor()
                            cursor.execute("DELETE FROM vocabulary WHERE id=?", (v_id,))
                            conn.commit(); conn.close(); st.rerun()

    with t3:
        st.subheader("Nạp Bài Đọc JSON")
        js_r = st.text_area("Dán JSON bài đọc tại đây:", height=200, key="txt_js_r")
        if st.button("Lưu bài đọc", key="btn_save_r"):
            if js_r.strip():
                try:
                    d = json.loads(js_r.strip())
                    conn = database.get_connection(); cursor = conn.cursor()
                    cursor.execute("INSERT INTO reading_lessons (level, title, content, grammar_points, quiz) VALUES (?,?,?,?,?)",
                                   (d.get("level","A1"), d.get("title",""), d.get("content",""), json.dumps(d.get("grammar_points",[])), json.dumps(d.get("quiz",[]))))
                    conn.commit(); conn.close(); st.success("Đã nạp bài đọc!"); st.rerun()
                except Exception as e: st.error(f"Lỗi JSON: {e}")

    with t4:
        st.subheader("Nạp Mảng Từ Vựng Hàng Loạt")
        js_v = st.text_area("Dán Mảng JSON từ vựng tại đây:", height=200, key="txt_js_v")
        if st.button("Đóng gói nạp hàng loạt", key="btn_save_v"):
            if js_v.strip():
                try:
                    v_list = json.loads(js_v.strip())
                    conn = database.get_connection(); cursor = conn.cursor()
                    for item in v_list:
                        cursor.execute("""
                            INSERT OR REPLACE INTO vocabulary 
                            (vocab_date, word, word_type, phonetic, meaning, prefix, suffix, funny_story, other_forms, context_easy, context_medium, context_hard)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (item.get('date', datetime.now().strftime('%Y-%m-%d')), item['word'], item.get('word_type',''), item['phonetic'], item['meaning'], item.get('prefix',''), item.get('suffix',''), item['funny_story'], item.get('other_forms',''), item['context_easy'], item['context_medium'], item['context_hard']))
                    conn.commit(); conn.close(); st.success("Đã nạp thành công bộ từ vựng!"); st.rerun()
                except Exception as e: st.error(f"Lỗi JSON: {e}")