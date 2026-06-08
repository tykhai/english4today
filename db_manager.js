class DatabaseManager {
    constructor() {
        // ĐIỀN THÔNG TIN SUPABASE CỦA BẠN VÀO ĐÂY ĐỂ KẾT NỐI THẬT
        this.supabaseUrl = "https://xgixilajyehjdcauoleh.supabase.co";
        this.supabaseKey = "sb_publishable_uyxVz0n48exFMwzRKeqOiQ_le0a8LUq";
        this.currentUser = JSON.parse(localStorage.getItem('user_session')) || null;
    }

    async init() {
        console.log("⚡ Hệ thống Database Cloud Supabase đã kích hoạt.");
    }

    // Hàm gọi API dùng chung để tương tác với Supabase không cần cài thư viện cồng kềnh
    async request(path, method = 'GET', body = null) {
        const url = `${this.supabaseUrl}/rest/v1/${path}`;
        const headers = {
            "apikey": this.supabaseKey,
            "Authorization": `Bearer ${this.supabaseKey}`,
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        };
        const config = { method, headers };
        if (body) config.body = JSON.stringify(body);

        try {
            const response = await fetch(url, config);
            if (!response.ok) throw new Error(await response.text());
            return await response.json();
        } catch (error) {
            console.error("Database Error:", error);
            showToast("❌ Lỗi kết nối Cơ sở dữ liệu Cloud!");
            return null;
        }
    }

    // ĐĂNG KÝ USER MỚI
    async register(username, password) {
        const existing = await this.request(`users?username=eq.${username}`);
        if (existing && existing.length > 0) {
            alert("❌ Tên tài khoản này đã tồn tại!");
            return false;
        }
        const newUser = { username, password_hash: password, role: 'learner', allow_reading_part: true, allow_vocab_part: true };
        const result = await this.request('users', 'POST', newUser);
        return result ? true : false;
    }

    // ĐĂNG NHẬP THẬT TỪ DATABASE
    async login(username, password) {
        const users = await this.request(`users?username=eq.${username}&password_hash=eq.${password}`);
        if (users && users.length > 0) {
            this.currentUser = users[0];
            localStorage.setItem('user_session', JSON.stringify(this.currentUser));
            return this.currentUser;
        }
        return null;
    }

    logout() {
        this.currentUser = null;
        localStorage.removeItem('user_session');
    }

    // LẤY DANH SÁCH TẤT CẢ USER (Dành cho Admin quản lý)
    async getAllUsers() {
        return await this.request('users?order=created_at.desc');
    }

    // CẬP NHẬT QUYỀN HẠN USER
    async updateUserPermissions(userId, updates) {
        return await this.request(`users?user_id=eq.${userId}`, 'PATCH', updates);
    }

    // XÓA USER
    async deleteUser(userId) {
        return await this.request(`users?user_id=eq.${userId}`, 'DELETE');
    }

    // LẤY BÀI ĐỌC THỰC TẾ
    async getReadingLessons(level) {
        const data = await this.request(`reading_lessons?level=eq.${level}&limit=1`);
        return data || [];
    }

    async saveLesson(lessonData) {
        return await this.request('reading_lessons', 'POST', lessonData);
    }

    async saveVocabulary(vocabData) {
        return await this.request('vocabularies', 'POST', vocabData);
    }
}