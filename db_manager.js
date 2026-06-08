class DatabaseManager {
    constructor() {
        // Cấu hình kết nối Supabase Cloud (Bạn thay URL và Key của bạn vào đây)
        this.supabaseUrl = "https://xgixilajyehjdcauoleh.supabase.co";
        this.supabaseKey = "sb_publishable_uyxVz0n48exFMwzRKeqOiQ_le0a8LUq";
        this.currentUser = JSON.parse(localStorage.getItem('user_session')) || null;
    }

    async init() {
        console.log("Database Cloud đã sẵn sàng kết nối.");
        // Code thực tế sẽ gọi fetch kiểm tra trạng thái network hoặc DB ở đây
    }

    // Logic Đăng nhập (Auth) trực tiếp vào DB
    async login(username, password) {
        // Mô phỏng API Auth từ Database Cloud bảo mật
        if(username === "admin" && password === "admin123") {
            this.currentUser = { user_id: "u1", username: "admin", role: "admin" };
        } else {
            this.currentUser = { user_id: "u2", username: "Khải Lê", role: "learner" };
        }
        localStorage.setItem('user_session', JSON.stringify(this.currentUser));
        return this.currentUser;
    }

    logout() {
        this.currentUser = null;
        localStorage.removeItem('user_session');
    }

    // Lấy bài đọc từ Database dựa trên Cấp độ
    async getReadingLessons(level) {
        // Gọi API Cloud lấy bài đọc theo điều kiện `level = level`
        return [
            {
                lesson_id: "l1", level: "B", title: "Ứng dụng AI trong Chăn nuôi Thủy sản 2026",
                content: "Artificial intelligence is expanding rapidly in aquaculture. Farmers are using smart sensors to monitor water minerals like Kaolin and Zeolite to maximize shrimp health.",
                grammar_points: [
                    { structures: "Present Continuous (S + is/are + V-ing)", explanation: "Diễn tả hành động đang tiến triển nhanh chóng (is expanding).", examples: ["The technology is developing day by day."] }
                ]
            }
        ];
    }

    // Lưu dữ liệu bài học do Admin nhập vào Cloud DB
    async saveLesson(lessonData) {
        showToast("💾 Đang lưu bài đọc mới lên Cloud Database...");
        console.log("POST to /reading_lessons", lessonData);
        return true;
    }

    async saveVocabulary(vocabData) {
        showToast("💾 Đang nạp bộ từ vựng mới vào Database...");
        console.log("POST to /vocabularies", vocabData);
        return true;
    }

    // THUẬT TOÁN SRS (Spaced Repetition System) - Xử lý khi user bấm nút "Thuộc" hoặc "Chưa thuộc"
    async updateProgress(vocabId, rating) {
        // rating: 'hard' (chưa thuộc), 'good' (mơ hồ), 'easy' (đã thuộc)
        let daysToAdd = 1;
        if (rating === 'good') daysToAdd = 3;
        if (rating === 'easy') daysToAdd = 7;

        let nextReview = new Date();
        nextReview.setDate(nextReview.getDate() + daysToAdd);

        showToast(`🔄 Đã cập nhật lịch ôn tập: Quay lại sau ${daysToAdd} ngày!`);
        // Đồng bộ lên bảng `learning_progress` trên Cloud
    }
}