class AdminController {
    async renderAdminPanel() {
        const container = document.getElementById('app-container');
        container.innerHTML = `
            <div class="space-y-8 max-w-6xl mx-auto">
                <div class="flex justify-between items-center border-b pb-4 border-slate-200">
                    <h2 class="text-2xl font-bold text-slate-900">🎛️ Hệ Thống Quản Trị Hệ Thống (ADMIN)</h2>
                    <button onclick="window.learnerCtrl.renderDashboard()" class="text-sm bg-slate-100 hover:bg-slate-200 text-slate-700 px-4 py-2 rounded-xl font-medium transition">Quay lại Dashboard</button>
                </div>

                <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
                    <h3 class="font-bold text-lg text-slate-900 mb-4">👥 Quản Lý Học Viên & Phân Quyền Học Phần</h3>
                    <div class="overflow-x-auto">
                        <table class="min-w-full divide-y divide-slate-200 text-sm">
                            <thead class="bg-slate-50 font-semibold text-slate-700">
                                <tr>
                                    <td class="p-3">Tên Người Dùng</td>
                                    <td class="p-3">Vai Trò</td>
                                    <td class="p-3">Học Phần 1 (Bài Đọc)</td>
                                    <td class="p-3">Học Phần 2 (Từ Vựng)</td>
                                    <td class="p-3 text-center">Hành Động</td>
                                </tr>
                            </thead>
                            <tbody id="admin-user-table-body" class="divide-y divide-slate-100">
                                <tr><td colspan="5" class="text-center p-4 text-slate-400">Đang tải danh sách học viên từ database Cloud...</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col">
                        <h3 class="font-bold text-lg mb-2 text-indigo-600">📚 Thêm Bài Đọc Mới (JSON)</h3>
                        <textarea id="json-reading-input" class="w-full flex-1 min-h-[200px] font-mono text-xs p-3 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500" placeholder='Dán chuỗi JSON bài đọc sinh ra từ AI vào đây...'></textarea>
                        <button onclick="window.adminCtrl.submitReading()" class="mt-4 w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2.5 rounded-xl transition">Nạp Bài Đọc</button>
                    </div>

                    <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col">
                        <h3 class="font-bold text-lg mb-2 text-emerald-600">📆 Thêm Từ Vựng Theo Ngày (JSON)</h3>
                        <textarea id="json-vocab-input" class="w-full flex-1 min-h-[200px] font-mono text-xs p-3 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500" placeholder='Dán chuỗi JSON từ vựng sinh ra từ AI vào đây...'></textarea>
                        <button onclick="window.adminCtrl.submitVocab()" class="mt-4 w-full bg-emerald-600 hover:bg-emerald-700 text-white font-medium py-2.5 rounded-xl transition">Nạp Từ Vựng</button>
                    </div>
                </div>
            </div>
        `;
        
        // Gọi nạp danh sách user ngay sau khi vẽ giao diện xong
        await this.loadUsersTable();
    }

    async loadUsersTable() {
        const users = await window.db.getAllUsers();
        const tbody = document.getElementById('admin-user-table-body');
        if(!users || users.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" class="text-center p-4 text-slate-400">Không có học viên nào.</td></tr>`;
            return;
        }

        tbody.innerHTML = users.map(u => `
            <tr class="hover:bg-slate-50 transition">
                <td class="p-3 font-medium text-slate-900">${u.username}</td>
                <td class="p-3 capitalize text-slate-600">${u.role}</td>
                <td class="p-3">
                    <input type="checkbox" ${u.allow_reading_part ? 'checked' : ''} 
                           onchange="window.adminCtrl.togglePermission('${u.user_id}', 'allow_reading_part', this.checked)"
                           class="w-4 h-4 text-indigo-600 border-slate-300 rounded focus:ring-indigo-500">
                </td>
                <td class="p-3">
                    <input type="checkbox" ${u.allow_vocab_part ? 'checked' : ''} 
                           onchange="window.adminCtrl.togglePermission('${u.user_id}', 'allow_vocab_part', this.checked)"
                           class="w-4 h-4 text-emerald-600 border-slate-300 rounded focus:ring-emerald-500">
                </td>
                <td class="p-3 text-center">
                    <button onclick="window.adminCtrl.deleteUser('${u.user_id}')" class="text-xs bg-rose-50 hover:bg-rose-100 text-rose-600 px-2.5 py-1.5 rounded-lg transition font-medium">Xóa Tài Khoản</button>
                </td>
            </tr>
        `).join('');
    }

    async togglePermission(userId, field, value) {
        const updates = {};
        updates[field] = value;
        const res = await window.db.updateUserPermissions(userId, updates);
        if(res) showToast("🔄 Đã cập nhật quyền học phần của User thành công!");
    }

    async deleteUser(userId) {
        if(confirm("❗ Bạn có chắc chắn muốn xóa vĩnh viễn tài khoản học viên này khỏi hệ thống không?")) {
            await window.db.deleteUser(userId);
            showToast("🗑️ Đã xóa user thành công.");
            this.loadUsersTable();
        }
    }

    async submitReading() {
        try {
            const rawJson = document.getElementById('json-reading-input').value;
            const parsed = JSON.parse(rawJson);
            await window.db.saveLesson(parsed);
            document.getElementById('json-reading-input').value = "";
            showToast("✅ Nạp thành công bài đọc lên Cloud!");
        } catch (e) { alert("❌ Lỗi định dạng cấu trúc JSON bài đọc!"); }
    }

    async submitVocab() {
        try {
            const rawJson = document.getElementById('json-vocab-input').value;
            const parsed = JSON.parse(rawJson);
            await window.db.saveVocabulary(parsed);
            document.getElementById('json-vocab-input').value = "";
            showToast("✅ Nạp thành công danh sách từ vựng!");
        } catch (e) { alert("❌ Lỗi định dạng cấu trúc JSON từ vựng!"); }
    }
}