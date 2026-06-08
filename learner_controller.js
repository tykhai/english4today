class LearnerController {
    // CHÈN THÊM HÀM NÀY VÀO TRÊN CÙNG CỦA CLASS LEARNERCONTROLLER
    renderAuthZone() {
        let authContainer = document.getElementById('auth-zone');
        // Nếu trong file HTML chưa có thẻ div id="auth-zone", hệ thống sẽ tự tạo một cái ở đầu trang
        if (!authContainer) {
            authContainer = document.createElement('div');
            authContainer.id = 'auth-zone';
            authContainer.className = 'max-w-6xl mx-auto px-4 pt-4 flex justify-end';
            document.body.insertBefore(authContainer, document.body.firstChild);
        }

        const user = window.db.currentUser;
        if (user) {
            authContainer.innerHTML = `
                <div class="flex items-center space-x-3 text-sm">
                    <span class="text-slate-600 font-medium">Tài khoản: <strong>${user.username}</strong></span>
                    <button onclick="window.learnerCtrl.logoutSubmit()" class="text-rose-600 hover:text-rose-700 font-semibold bg-rose-50 px-3 py-1.5 rounded-xl transition">Đăng Xuất 🚪</button>
                </div>
            `;
        } else {
            authContainer.innerHTML = `
                <button onclick="window.learnerCtrl.triggerLogin()" class="bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold px-4 py-2 rounded-xl transition shadow-sm">Đăng Nhập Hệ Thống</button>
            `;
        }
    }

    // Tiện tay thêm luôn hàm logoutSubmit() hỗ trợ cho nút Đăng Xuất ở trên
    logoutSubmit() {
        window.db.logout();
        this.renderDashboard();
        showToast("🔒 Đã đăng xuất an toàn.");
    }
    renderDashboard() {
        this.renderAuthZone();
        const container = document.getElementById('app-container');
        const user = window.db.currentUser;

        if (!user) {
            container.innerHTML = `
                <div class="text-center py-20 bg-white rounded-3xl border border-slate-200 shadow-sm max-w-xl mx-auto space-y-4">
                    <div class="text-5xl">🔐</div>
                    <h2 class="text-2xl font-bold text-slate-800">Hệ Thống Học Ngữ Liệu Thông Minh</h2>
                    <p class="text-slate-500 text-sm">Vui lòng đăng nhập bằng tài khoản được cấp để bắt đầu bài học.</p>
                    <button onclick="window.learnerCtrl.triggerLogin()" class="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold px-8 py-3 rounded-xl transition shadow-md">Đăng Nhập Ngay</button>
                </div>
            `;
            return;
        }

        container.innerHTML = `
            <div class="space-y-8">
                <div class="bg-gradient-to-r from-slate-900 to-indigo-900 rounded-3xl p-6 text-white shadow-lg flex justify-between items-center">
                    <div>
                        <h2 class="text-2xl font-bold">Chào mừng trở lại, ${user.username}! 🔥</h2>
                        <p class="text-white/60 text-sm mt-1">Quyền hạn: <span class="bg-indigo-500/30 text-indigo-300 px-2 py-0.5 rounded text-xs capitalize font-bold">${user.role}</span></p>
                    </div>
                    <button onclick="window.adminCtrl.openChangePasswordModal('${user.user_id}')" class="text-xs bg-white/10 hover:bg-white/20 px-3 py-2 rounded-xl transition">🔒 Đổi mật khẩu</button>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <!-- PHẦN 1: BÀI ĐỌC -->
                    ${user.allow_reading_part || user.role === 'admin' ? `
                    <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition cursor-pointer" onclick="window.learnerCtrl.startReadingView('B')">
                        <div class="text-3xl mb-2">📚</div>
                        <h3 class="font-bold text-lg text-slate-900">Phần 1: Luyện Bài Đọc Theo Cấp Độ</h3>
                        <p class="text-slate-500 text-sm mt-1">Đọc hiểu ngữ liệu ngành, nhấp chuột tra từ vựng, phân tích cú pháp chi tiết.</p>
                    </div>
                    ` : `
                    <div class="bg-slate-100 p-6 rounded-2xl border border-slate-200 opacity-60 cursor-not-allowed">
                        <div class="text-3xl mb-2">🔒</div>
                        <h3 class="font-bold text-lg text-slate-400">Phần 1: Bài Đọc (Bị Khóa)</h3>
                        <p class="text-slate-400 text-sm mt-1">Tài khoản chưa được kích hoạt quyền truy cập phần này.</p>
                    </div>
                    `}

                    <!-- PHẦN 2: TỪ VỰNG -->
                    ${user.allow_vocab_part || user.role === 'admin' ? `
                    <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition cursor-pointer" onclick="window.learnerCtrl.startVocabView('Success')">
                        <div class="text-3xl mb-2">🧠</div>
                        <h3 class="font-bold text-lg text-slate-900">Phần 2: Từ Vựng & Sơ Đồ Tư Duy</h3>
                        <p class="text-slate-500 text-sm mt-1">Học từ loại, ghi nhớ qua cốt truyện hài hước và ngữ cảnh 3 cấp độ.</p>
                    </div>
                    ` : `
                    <div class="bg-slate-100 p-6 rounded-2xl border border-slate-200 opacity-60 cursor-not-allowed">
                        <div class="text-3xl mb-2">🔒</div>
                        <h3 class="font-bold text-lg text-slate-400">Phần 2: Từ Vựng (Bị Khóa)</h3>
                        <p class="text-slate-400 text-sm mt-1">Tài khoản chưa được kích hoạt quyền truy cập phần này.</p>
                    </div>
                    `}

                    <!-- ĐƯỜNG VÀO ADMIN -->
                    ${user.role === 'admin' ? `
                    <div class="bg-amber-50 p-6 rounded-2xl border-2 border-dashed border-amber-300 shadow-sm hover:shadow-md transition cursor-pointer" onclick="window.adminCtrl.renderAdminPanel()">
                        <div class="text-3xl mb-2">⚙️</div>
                        <h3 class="font-bold text-lg text-amber-800">Bảng Quản Trị Hệ Thống</h3>
                        <p class="text-amber-600 text-sm mt-1">Quản lý, tạo/xóa/khóa thành viên, cấp quyền học, nạp bài học mới.</p>
                    </div>
                    ` : ''}
                </div>
            </div>
        `;
    }

    async startReadingView(level) {
        const lessons = await window.db.getReadingLessons(level);
        if (lessons.length === 0) {
            alert("Hiện tại chưa có dữ liệu bài đọc cấp độ này trên Database. Vui lòng vào Admin nạp dữ liệu mẫu.");
            return;
        }
        const lesson = lessons[0];
        const container = document.getElementById('app-container');
        
        container.innerHTML = `
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div class="lg:col-span-2 bg-white p-8 rounded-2xl border border-slate-200 shadow-sm">
                    <button onclick="window.learnerCtrl.renderDashboard()" class="text-sm text-indigo-600 mb-4 font-medium block">← Quay lại màn hình chính</button>
                    <span class="bg-indigo-100 text-indigo-700 text-xs px-2.5 py-1 rounded-full font-bold uppercase tracking-wider">Cấp độ ${lesson.level}</span>
                    <h2 class="text-2xl font-bold text-slate-900 mt-2 mb-6">${lesson.title}</h2>
                    
                    <!-- Đoạn văn được bọc xử lý phân tách từng từ để có thể click tương tác -->
                    <div class="font-reading text-xl text-slate-700 leading-relaxed space-y-4">
                        ${this.highlightContent(lesson.content)}
                    </div>
                </div>
                
                <div class="bg-slate-900 text-slate-100 p-6 rounded-2xl shadow-sm flex flex-col justify-between">
                    <div>
                        <h3 class="text-amber-400 font-bold text-lg mb-4 flex items-center">💡 Cấu trúc Cú Pháp & Ngữ Pháp</h3>
                        <div class="space-y-4">
                            <h4 class="font-bold text-white text-base">${lesson.grammar_points[0]?.structures || 'N/A'}</h4>
                            <p class="text-sm text-slate-400 leading-relaxed">${lesson.grammar_points[0]?.explanation || ''}</p>
                            <div class="bg-white/5 border-l-2 border-amber-400 p-3 rounded-r-xl italic text-sm text-slate-300">
                                "${lesson.grammar_points[0]?.examples[0] || ''}"
                            </div>
                        </div>
                    </div>
                    <div class="mt-8 border-t border-white/10 pt-4 text-xs text-slate-500">Mẹo: Bạn có thể click chuột vào BẤT KỲ TỪ NÀO trong bài văn để tra cứu nghĩa từ DB Cloud và nghe phát âm.</div>
                </div>
            </div>
        `;
    }

    // Tự động phân tách toàn bộ văn bản thành từng từ độc lập để từ nào cũng bấm nghe/đọc được
    highlightContent(content) {
        const words = content.split(/(\s+|,|\.|\?|!|;|:|"|')/);
        return words.map(w => {
            // Lọc bỏ ký tự đặc biệt, chỉ lấy chữ để tra cứu
            const cleanWord = w.replace(/[^a-zA-Z]/g, '');
            if(cleanWord.length > 0) {
                return `<span class="hover:bg-amber-100 hover:text-amber-900 rounded cursor-pointer transition px-0.5 border-b border-transparent hover:border-amber-400" onclick="window.learnerCtrl.showWordPopup(event, '${cleanWord}')">${w}</span>`;
            }
            return w;
        }).join('');
    }

    // Popup đọc từ vựng động kết nối Database thật
    async showWordPopup(event, word) {
        event.stopPropagation();
        const oldPopup = document.getElementById('word-reader-popup');
        if (oldPopup) oldPopup.remove();

        // Tự động kích hoạt giọng đọc tiếng Anh ngay khi bấm vào từ (Yêu cầu 3)
        this.speak(word);

        // Truy vấn dữ liệu từ khóa từ database thật
        const dbWord = await window.db.getVocabularyWord(word);
        
        const popup = document.createElement('div');
        popup.id = 'word-reader-popup';
        popup.className = 'absolute bg-slate-900 text-white p-4 rounded-xl shadow-2xl z-50 text-sm max-w-xs space-y-2 border border-slate-700';
        
        if (dbWord) {
            popup.innerHTML = `
                <div class="flex justify-between items-center space-x-4">
                    <span class="font-bold text-amber-400 text-base">${dbWord.word}</span>
                    <span class="text-xs bg-slate-700 text-slate-300 px-2 py-0.5 rounded italic font-medium">${dbWord.word_type || 'Từ loại'}</span>
                </div>
                <div class="text-xs text-slate-400 font-mono">${dbWord.phonetic || '/.../'}</div>
                <div class="text-slate-200 border-t border-slate-700 pt-1.5 font-medium">${dbWord.meaning}</div>
                <div class="text-xs bg-indigo-950/50 p-2 rounded text-indigo-300 border border-indigo-900/40 italic">💬 Ngữ cảnh (Dễ): ${dbWord.context_easy || 'Chưa cập nhật'}</div>
            `;
        } else {
            popup.innerHTML = `
                <div class="flex justify-between items-center">
                    <span class="font-bold text-slate-400 text-base">${word}</span>
                    <span class="text-xs text-slate-500">Hệ thống âm thanh</span>
                </div>
                <div class="text-xs text-slate-400 italic pt-1 border-t border-slate-800">Đang phát âm phát luồng trực tiếp...</div>
            `;
        }

        document.body.appendChild(popup);
        popup.style.left = `${event.pageX - (popup.offsetWidth / 2)}px`;
        popup.style.top = `${event.pageY - popup.offsetHeight - 12}px`;

        setTimeout(() => {
            const closePopup = () => { popup.remove(); document.removeEventListener('click', closePopup); };
            document.addEventListener('click', closePopup);
        }, 150);
    }

    // Hiển thị Chi Tiết Từ Loại và 3 Cấp Độ Ngữ Cảnh Dễ - Vừa - Khó (Yêu cầu 2)
    async startVocabView(wordKeyword = "Success") {
        const container = document.getElementById('app-container');
        const vocabData = await window.db.getVocabularyWord(wordKeyword);

        container.innerHTML = `
            <div class="space-y-6">
                <div class="flex justify-between items-center">
                    <button onclick="window.learnerCtrl.renderDashboard()" class="text-sm text-indigo-600 font-medium">← Quay lại</button>
                    <h2 class="text-xl font-bold text-slate-900">🧠 Sơ đồ cấu trúc từ vựng nâng cao</h2>
                </div>
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    <div class="lg:col-span-1 bg-white h-[450px] rounded-2xl border border-slate-200 shadow-sm" id="mindmap-canvas"></div>
                    
                    <div class="lg:col-span-2 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between space-y-6">
                        ${vocabData ? `
                        <div>
                            <div class="flex items-baseline justify-between border-b pb-3 border-slate-100">
                                <div class="flex items-center space-x-3">
                                    <h3 class="text-3xl font-bold text-indigo-600">${vocabData.word}</h3>
                                    <span class="bg-indigo-100 text-indigo-700 font-bold text-xs px-2.5 py-1 rounded-lg uppercase tracking-wide">${vocabData.word_type}</span>
                                </div>
                                <button onclick="window.learnerCtrl.speak('${vocabData.word}')" class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-1.5 rounded-xl text-xs font-semibold">🔊 Phát Âm</button>
                            </div>
                            
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                                <div>
                                    <span class="text-xs font-bold text-slate-400 uppercase tracking-wider block">Phiên âm chuẩn</span>
                                    <p class="font-mono text-slate-700 text-sm mt-0.5">${vocabData.phonetic}</p>
                                    
                                    <span class="text-xs font-bold text-slate-400 uppercase tracking-wider block mt-3">Ý nghĩa bản dịch</span>
                                    <p class="text-slate-900 font-semibold text-base mt-0.5">${vocabData.meaning}</p>
                                </div>
                                <div class="bg-amber-50 rounded-xl p-3 border border-amber-200">
                                    <span class="text-xs uppercase font-bold text-amber-800 tracking-wider block">💡 Mẹo học cốt truyện:</span>
                                    <p class="text-slate-700 text-sm leading-relaxed italic mt-1">"${vocabData.funny_story || 'Chưa cập nhật mẹo kể chuyện.'}"</p>
                                </div>
                            </div>

                            <!-- KHỐI HIỂN THỊ NGỮ CẢNH THEO 3 CẤP ĐỘ -->
                            <div class="mt-6 space-y-3">
                                <span class="text-xs font-bold text-slate-500 uppercase tracking-wider block">🎯 Cách dùng từ theo ngữ cảnh (3 Cấp độ):</span>
                                
                                <div class="bg-emerald-50 border-l-4 border-emerald-500 p-3 rounded-r-xl">
                                    <span class="text-xs font-bold text-emerald-800 uppercase block">Cấp độ 1: DỄ (Câu đơn, giao tiếp cơ bản)</span>
                                    <p class="text-slate-700 text-sm mt-0.5 font-medium">${vocabData.context_easy || 'Chưa nạp ngữ cảnh dễ'}</p>
                                </div>

                                <div class="bg-blue-50 border-l-4 border-blue-500 p-3 rounded-r-xl">
                                    <span class="text-xs font-bold text-blue-800 uppercase block">Cấp độ 2: VỪA (Cấu trúc học thuật, công việc)</span>
                                    <p class="text-slate-700 text-sm mt-0.5 font-medium">${vocabData.context_medium || 'Chưa nạp ngữ cảnh vừa'}</p>
                                </div>

                                <div class="bg-rose-50 border-l-4 border-rose-500 p-3 rounded-r-xl">
                                    <span class="text-xs font-bold text-rose-800 uppercase block">Cấp độ 3: KHÓ (Văn cảnh chuyên ngành, phân tích sâu)</span>
                                    <p class="text-slate-700 text-sm mt-0.5 font-medium">${vocabData.context_hard || 'Chưa nạp ngữ cảnh khó'}</p>
                                </div>
                            </div>
                        </div>
                        ` : `
                        <div class="text-center py-12 text-slate-400">Không tìm thấy dữ liệu mở rộng cho từ này. Vui lòng sử dụng Form nạp dữ liệu Admin theo cấu trúc mới ở dưới.</div>
                        `}
                    </div>
                </div>
            </div>
        `;
        this.drawMindmap(wordKeyword);
    }

    drawMindmap(centerWord) {
        const container = document.getElementById('mindmap-canvas');
        const data = {
            nodes: new vis.DataSet([
                { id: 1, label: `${centerWord}\n(Từ khóa)`, color: '#e0e7ff', font: { size: 16, bold: true } },
                { id: 2, label: 'Đồng nghĩa\n(Synonym)', color: '#ecfdf5' },
                { id: 3, label: 'Trái nghĩa\n(Antonym)', color: '#fef2f2' }
            ]),
            edges: new vis.DataSet([{ from: 1, to: 2 }, { from: 1, to: 3 }])
        };
        new vis.Network(container, data, { edges: { color: '#cbd5e1' } });
    }

    async triggerLogin() {
        const user = prompt("Nhập tài khoản:");
        const pass = prompt("Nhập mật khẩu:");
        if(!user || !pass) return;
        
        const u = await window.db.login(user, pass);
        if (u) {
            this.renderDashboard();
            showToast("👋 Đăng nhập thành công!");
        }
    }

    speak(text) {
        if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'en-US';
            utterance.rate = 0.85;
            window.speechSynthesis.speak(utterance);
        }
    }
}