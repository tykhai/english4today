class AdminController {
    async renderAdminPanel() {
        const container = document.getElementById('app-container');
        container.innerHTML = `
            <div class="space-y-8 max-w-6xl mx-auto">
                <div class="flex justify-between items-center border-b pb-4 border-slate-200">
                    <h2 class="text-2xl font-bold text-slate-900">🎛️ Bảng Điều Hành Quản Trị Hệ Thống (ADMIN)</h2>
                    <button onclick="window.learnerCtrl.renderDashboard()" class="text-sm bg-slate-100 hover:bg-slate-200 text-slate-700 px-4 py-2 rounded-xl font-medium transition">Quay lại Dashboard</button>
                </div>

                <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    <!-- KHỐI TẠO USER MỚI (Yêu cầu 1) -->
                    <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
                        <h3 class="font-bold text-base text-slate-900 flex items-center">➕ Cấp Tài Khoản Mới</h3>
                        <div>
                            <label class="text-xs font-semibold text-slate-500 block mb-1">Tên đăng nhập (Username)</label>
                            <input id="new-user-name" type="text" class="w-full border p-2 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500 outline-none">
                        </div>
                        <div>
                            <label class="text-xs font-semibold text-slate-500 block mb-1">Mật khẩu khởi tạo</label>
                            <input id="new-user-pass" type="password" class="w-full border p-2 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500 outline-none">
                        </div>
                        <div>
                            <label class="text-xs font-semibold text-slate-500 block mb-1">Vai trò tài khoản</label>
                            <select id="new-user-role" class="w-full border p-2 rounded-xl text-sm bg-white">
                                <option value="learner">Học Sinh (Learner)</option>
                                <option value="admin">Quản Trị Viên (Admin)</option>
                            </select>
                        </div>
                        <button onclick="window.adminCtrl.createUserSubmit()" class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 rounded-xl transition text-sm">Tạo Thành Viên</button>
                    </div>

                    <!-- KHỐI DANH SÁCH USER VÀ PHÂN QUYỀN / KHÓA (Yêu cầu 1) -->
                    <div class="lg:col-span-2 bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col">
                        <h3 class="font-bold text-base text-slate-900 mb-3">👥 Danh Sách Thành Viên & Phân Quyền</h3>
                        <div class="overflow-x-auto flex-1">
                            <table class="min-w-full divide-y divide-slate-200 text-xs">
                                <thead class="bg-slate-50 font-bold text-slate-600">
                                    <tr>
                                        <td class="p-2.5">Tên User</td>
                                        <td class="p-2.5">Vai trò</td>
                                        <td class="p-2.5 text-center">P1 (Đọc)</td>
                                        <td class="p-2.5 text-center">P2 (Từ vựng)</td>
                                        <td class="p-2.5 text-center">Khóa Học</td>
                                        <td class="p-2.5 text-center">Hành động</td>
                                    </tr>
                                </thead>
                                <tbody id="admin-user-table-body" class="divide-y divide-slate-100">
                                    <tr><td colspan="6" class="text-center p-4">Đang đồng bộ dữ liệu...</td></tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <!-- BỘ FORM NẠP DỮ LIỆU JSON THEO TIÊU CHUẨN MỚI -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col">
                        <h3 class="font-bold text-lg mb-2 text-indigo-600">📚 Nạp Bài Đọc Mới (JSON)</h3>
                        <textarea id="json-reading-input" class="w-full flex-1 min-h-[180px] font-mono text-xs p-3 border border-slate-200 rounded-xl outline-none" placeholder="Dán cấu trúc JSON bài đọc vào đây..."></textarea>
                        <button onclick="window.adminCtrl.submitReading()" class="mt-4 w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 rounded-xl transition">Nạp Lên Hệ Thống</button>
                    </div>

                    <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col">
                        <h3 class="font-bold text-lg mb-2 text-emerald-600">🧠 Nạp Từ Vựng Nâng Cao 3 Cấp Độ (JSON)</h3>
                        <textarea id="json-vocab-input" class="w-full flex-1 min-h-[180px] font-mono text-xs p-3 border border-slate-200 rounded-xl outline-none" placeholder="Dán cấu trúc JSON từ vựng có word_type và ngữ cảnh 3 cấp độ vào đây..."></textarea>
                        <button onclick="window.adminCtrl.submitVocab()" class="mt-4 w-full bg-emerald-600 hover:bg-emerald-700 text-white font-medium py-2 rounded-xl transition">Nạp Lên Hệ Thống</button>
                    </div>
                </div>
            </div>
        `;
        await this.loadUsersTable();
    }

    async loadUsersTable() {
        const users = await window.db.getAllUsers();
        const tbody = document.getElementById('admin-user-table-body');
        if(!users) return;

        tbody.innerHTML = users.map(u => `
            <tr class="hover:bg-slate-50 transition">
                <td class="p-2.5 font-bold text-slate-800">${u.username}</td>
                <td class="p-2.5 capitalize text-slate-500">${u.role}</td>
                <td class="p-2.5 text-center">
                    <input type="checkbox" ${u.allow_reading_part ? 'checked' : ''} onchange="window.adminCtrl.togglePermission('${u.user_id}', 'allow_reading_part', this.checked)">
                </td>
                <td class="p-2.5 text-center">
                    <input type="checkbox" ${u.allow_vocab_part ? 'checked' : ''} onchange="window.adminCtrl.togglePermission('${u.user_id}', 'allow_vocab_part', this.checked)">
                </td>
                <td class="p-2.5 text-center">
                    <!-- KHÓA USER TẠM THỜI (Yêu cầu 1) -->
                    <input type="checkbox" ${u.is_banned ? 'checked' : ''} onchange="window.adminCtrl.togglePermission('${u.user_id}', 'is_banned', this.checked)" class="accent-rose-600">
                </td>
                <td class="p-2.5 text-center space-x-1">
                    <button onclick="window.adminCtrl.openChangePasswordModal('${u.user_id}')" class="text-[10px] bg-slate-100 text-slate-600 px-2 py-1 rounded hover:bg-slate-200">Đổi Pass</button>
                    <button onclick="window.adminCtrl.deleteUser('${u.user_id}')" class="text-[10px] bg-rose-50 text-rose-600 px-2 py-1 rounded hover:bg-rose-100">Xóa</button>
                </td>
            </tr>
        `).join('');
    }

    async createUserSubmit() {
        const name = document.getElementById('new-user-name').value.trim();
        const pass = document.getElementById('new-user-pass').value.trim();
        const role = document.getElementById('new-user-role').value;
        if(!name || !pass) { alert("Vui lòng nhập đủ thông tin!"); return; }

        const res = await window.db.adminCreateUser(name, pass, role);
        if(res.success) {
            alert("🎉 Đã khởi tạo thành viên thành công!");
            document.getElementById('new-user-name').value = "";
            document.getElementById('new-user-pass').value = "";
            this.loadUsersTable();
        } else { alert("❌ Lỗi: " + res.msg); }
    }

    async openChangePasswordModal(userId) {
        const newPass = prompt("Nhập mật khẩu mới cho tài khoản này:");
        if (!newPass || newPass.trim().length === 0) return;
        
        const res = await window.db.changePassword(userId, newPass.trim());
        if(res) alert("🔒 Đã đổi mật khẩu tài khoản thành công trên Cloud!");
    }

    async togglePermission(userId, field, value) {
        const updates = {}; updates[field] = value;
        await window.db.updateUserPermissions(userId, updates);
        showToast("🔄 Trạng thái quyền hạn đã đồng bộ về Cloud.");
    }

    async deleteUser(userId) {
        if(confirm("Xóa vĩnh viễn tài khoản này?")) {
            await window.db.deleteUser(userId);
            this.loadUsersTable();
        }
    }

    async submitReading() {
        try {
            const parsed = JSON.parse(document.getElementById('json-reading-input').value);
            await window.db.saveLesson(parsed);
            document.getElementById('json-reading-input').value = "";
            alert("✅ Thành công!");
        } catch (e) { alert("JSON sai định dạng!"); }
    }

    async submitVocab() {
        try {
            const parsed = JSON.parse(document.getElementById('json-vocab-input').value);
            await window.db.saveVocabulary(parsed);
            document.getElementById('json-vocab-input').value = "";
            alert("✅ Thành công!");
        } catch (e) { alert("JSON sai định dạng!"); }
    }
}