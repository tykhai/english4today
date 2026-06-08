class AdminController {
    renderAdminPanel() {
        const container = document.getElementById('app-container');
        container.innerHTML = `
            <div class="space-y-6 max-w-4xl mx-auto">
                <div class="flex justify-between items-center border-b pb-4 border-slate-200">
                    <h2 class="text-2xl font-bold text-slate-900">🎛️ Khối Quản Trị Dữ Liệu Học</h2>
                    <button onclick="window.learnerCtrl.renderDashboard()" class="text-sm bg-slate-100 hover:bg-slate-200 text-slate-700 px-3 py-2 rounded-xl font-medium transition">Quay lại trang học</button>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col">
                        <h3 class="font-bold text-lg mb-3 text-indigo-600">📚 Thêm Bài Đọc Mới</h3>
                        <p class="text-xs text-slate-400 mb-4">Dán chuỗi JSON sinh ra từ Prompt AI vào đây để phân tích.</p>
                        <textarea id="json-reading-input" class="w-full flex-1 min-h-[250px] font-mono text-xs p-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:outline-none" placeholder='{"reading_id": "...", "level": "A", ...}'></textarea>
                        <button onclick="window.adminCtrl.submitReading()" class="mt-4 w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-3 rounded-xl transition">Nạp dữ liệu bài đọc</button>
                    </div>

                    <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col">
                        <h3 class="font-bold text-lg mb-3 text-emerald-600">📆 Thêm Từ Vựng Theo Ngày</h3>
                        <p class="text-xs text-slate-400 mb-4">Quản lý từ 10-30 từ theo sơ đồ tư duy hài hước.</p>
                        <textarea id="json-vocab-input" class="w-full flex-1 min-h-[250px] font-mono text-xs p-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:outline-none" placeholder='{"day_id": "DAY_01", "vocab_list": [...] }'></textarea>
                        <button onclick="window.adminCtrl.submitVocab()" class="mt-4 w-full bg-emerald-600 hover:bg-emerald-700 text-white font-medium py-3 rounded-xl transition">Nạp dữ liệu từ vựng</button>
                    </div>
                </div>
            </div>
        `;
    }

    async submitReading() {
        try {
            const rawJson = document.getElementById('json-reading-input').value;
            const parsed = JSON.parse(rawJson);
            await window.db.saveLesson(parsed);
            document.getElementById('json-reading-input').value = "";
            showToast("✅ Nạp bài đọc thành công lên Cloud!");
        } catch (e) {
            alert("❌ Định dạng dữ liệu JSON không hợp lệ, vui lòng kiểm tra kỹ lại!");
        }
    }

    async submitVocab() {
        try {
            const rawJson = document.getElementById('json-vocab-input').value;
            const parsed = JSON.parse(rawJson);
            await window.db.saveVocabulary(parsed);
            document.getElementById('json-vocab-input').value = "";
            showToast("✅ Nạp bộ từ vựng mới thành công!");
        } catch (e) {
            alert("❌ Định dạng dữ liệu JSON không hợp lệ!");
        }
    }
}