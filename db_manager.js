
class DatabaseManager {
    constructor() {
        this.supabaseUrl = "https://xgixilajyehjdcauoleh.supabase.co";
        this.supabaseKey = "sb_publishable_uyxVz0n48exFMwzRKeqOiQ_le0a8LUq";
        this.currentUser = JSON.parse(localStorage.getItem('user_session')) || null;
    }

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
            return null;
        }
    }

async login(username, password) {
    try {
        // Gọi trực tiếp fetch tới Supabase để kiểm soát 100% dữ liệu trả về
        const response = await fetch(`${this.supabaseUrl}/rest/v1/users?username=eq.${username}&password_hash=eq.${password}`, {
            method: 'GET',
            headers: {
                'apikey': this.supabaseKey,
                'Authorization': `Bearer ${this.supabaseKey}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            console.error("🚨 Supabase trả về lỗi HTTP:", response.status);
            return null;
        }

        // Bóc tách mảng dữ liệu JSON thật
        const users = await response.json();
        console.log("🔍 Dữ liệu mảng nhận được sau khi ép kiểu JSON:", users);

        // Kiểm tra xem mảng có phần tử nào trùng khớp không
        if (users && users.length > 0) {
            const userAccount = users[0];
            
            // Lưu thông tin User đăng nhập thành công vào hệ thống
            this.currentUser = userAccount;
            localStorage.setItem('user_session', JSON.stringify(this.currentUser));
            
            return this.currentUser; 
        }
        
        // Nếu mảng rỗng []
        console.log("⚠️ Mảng trả về rỗng. Tài khoản hoặc mật khẩu không khớp trong DB.");
        return null; 
    } catch (err) {
        console.error("Lỗi nghiêm trọng tại hàm login():", err);
        return null;
    }
}

    logout() {
        this.currentUser = null;
        localStorage.removeItem('user_session');
    }

    // ADMIN: Tạo trực tiếp User (Học sinh hoặc Quản trị) không cần qua form đăng ký tự do
    async adminCreateUser(username, password, role) {
        const existing = await this.request(`users?username=eq.${username}`);
        if (existing && existing.length > 0) return { success: false, msg: "Tài khoản đã tồn tại!" };
        
        const newUser = { 
            username, 
            password_hash: password, 
            role: role, 
            allow_reading_part: true, 
            allow_vocab_part: true,
            is_banned: false 
        };
        const res = await this.request('users', 'POST', newUser);
        return res ? { success: true } : { success: false, msg: "Lỗi hệ thống Cloud!" };
    }

    // ADMIN & USER: Thay đổi mật khẩu tài khoản
    async changePassword(userId, newPassword) {
        return await this.request(`users?user_id=eq.${userId}`, 'PATCH', { password_hash: newPassword });
    }

    async getAllUsers() {
        return await this.request('users?order=created_at.desc');
    }

    async updateUserPermissions(userId, updates) {
        return await this.request(`users?user_id=eq.${userId}`, 'PATCH', updates);
    }

    async deleteUser(userId) {
        return await this.request(`users?user_id=eq.${userId}`, 'DELETE');
    }

    async getReadingLessons(level) {
        return await this.request(`reading_lessons?level=eq.${level}&limit=1`) || [];
    }

    // LẤY THÔNG TIN TỪ VỰNG DỰA VÀO TỪ KHÓA ĐỂ LÀM POPUP HOẶC MINDMAP
    async getVocabularyWord(word) {
        const data = await this.request(`vocabularies?word=ilike.${word}`);
        return data && data.length > 0 ? data[0] : null;
    }

    async saveLesson(lessonData) {
        return await this.request('reading_lessons', 'POST', lessonData);
    }

    async saveVocabulary(vocabData) {
        return await this.request('vocabularies', 'POST', vocabData);
    }
}