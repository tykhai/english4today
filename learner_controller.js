class LearnerController {
    renderDashboard() {
        this.renderAuthZone();
        const container = document.getElementById('app-container');
        const user = window.db.currentUser;
        container.innerHTML = `
            <div class="space-y-8">
                <div class="bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 rounded-3xl p-6 text-white shadow-lg">
                    <h2 class="text-2xl font-bold">Chào mừng bạn trở lại học tập! 🔥</h2>
                    <p class="text-white/80 text-sm mt-1">Hôm nay bạn đang đăng nhập với tư cách: <b class="text-amber-300">${user ? user.username : 'Khách'}</b></p>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition cursor-pointer" onclick="window.learnerCtrl.startReadingView('B')">
                        <div class="text-3xl mb-2">📚</div>
                        <h3 class="font-bold text-lg text-slate-900">Luyện Bài Đọc Theo Cấp Độ</h3>
                        <p class="text-slate-500 text-sm mt-1">Học ngữ pháp, tra cứu trực tiếp từ vựng ngay trong ngữ cảnh.</p>
                    </div>

                    <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition cursor-pointer" onclick="window.learnerCtrl.startVocabView()">
                        <div class="text-3xl mb-2">🧠</div>
                        <h3 class="font-bold text-lg text-slate-900">Từ Vựng & Sơ Đồ Tư Duy</h3>
                        <p class="text-slate-500 text-sm mt-1">Mẹo học hài hước thông qua cốt truyện, sơ đồ tư duy rực rỡ.</p>
                    </div>

                    ${user && user.role === 'admin' ? `
                    <div class="bg-amber-50 p-6 rounded-2xl border-2 border-dashed border-amber-300 shadow-sm hover:shadow-md transition cursor-pointer" onclick="window.adminCtrl.renderAdminPanel()">
                        <div class="text-3xl mb-2">⚙️</div>
                        <h3 class="font-bold text-lg text-amber-800">Bảng Quản Trị (Admin)</h3>
                        <p class="text-amber-600 text-sm mt-1">Khu vực dành riêng cho bạn để nạp thêm bài đọc, sửa danh sách từ vựng.</p>
                    </div>
                    ` : ''}
                </div>
            </div>
        `;
    }

    async startReadingView(level) {
        const lessons = await window.db.getReadingLessons(level);
        const lesson = lessons[0];
        const container = document.getElementById('app-container');
        
        container.innerHTML = `
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div class="lg:col-span-2 bg-white p-8 rounded-2xl border border-slate-200 shadow-sm">
                    <button onclick="window.learnerCtrl.renderDashboard()" class="text-sm text-indigo-600 mb-4 font-medium block">← Quay lại màn hình chính</button>
                    <span class="bg-indigo-100 text-indigo-700 text-xs px-2.5 py-1 rounded-full font-bold uppercase tracking-wider">Cấp độ ${lesson.level}</span>
                    <h2 class="text-2xl font-bold text-slate-900 mt-2 mb-6">${lesson.title}</h2>
                    <div class="font-reading text-xl text-slate-700 leading-relaxed space-y-4">
                        ${this.highlightContent(lesson.content)}
                    </div>
                </div>
                <div class="bg-slate-900 text-slate-100 p-6 rounded-2xl shadow-sm flex flex-col justify-between">
                    <div>
                        <h3 class="text-amber-400 font-bold text-lg mb-4 flex items-center">💡 Cấu trúc Ngữ Pháp chính</h3>
                        <div class="space-y-4">
                            <h4 class="font-bold text-white text-base">${lesson.grammar_points[0].structures}</h4>
                            <p class="text-sm text-slate-400 leading-relaxed">${lesson.grammar_points[0].explanation}</p>
                            <div class="bg-white/5 border-l-2 border-amber-400 p-3 rounded-r-xl italic text-sm text-slate-300">
                                " ${lesson.grammar_points[0].examples[0]} "
                            </div>
                        </div>
                    </div>
                    <div class="mt-8 border-t border-white/10 pt-4 text-xs text-slate-500">Mẹo: Click trực tiếp vào các từ vựng được tô đậm trong bài để xem nhanh nghĩa.</div>
                </div>
            </div>
        `;
    }

    highlightContent(content) {
        // Tự động bọc các từ khóa bằng thẻ span có chứa class tương tác và thuộc tính dữ liệu
        return content.replace(/(Kaolin|Zeolite|expanding)/g, 
            `<span class="bg-amber-100 text-amber-900 font-bold px-1 rounded cursor-pointer border-b-2 border-amber-400 hover:bg-amber-200 transition" 
                   onclick="window.learnerCtrl.showWordPopup(event, '$1')">$1</span>`);
    }

    // Hàm hiển thị Popup giải nghĩa ngay tại vị trí Click
    showWordPopup(event, word) {
        // Xóa popup cũ nếu có
        const oldPopup = document.getElementById('word-reader-popup');
        if (oldPopup) oldPopup.remove();

        // Dữ liệu mẫu (Khi chạy thật sẽ fetch từ bảng vocabularies của database dựa vào 'word')
        const dictionary = {
            "expanding": { phonetic: "/ɪkˈspændɪŋ/", meaning: "Mở rộng, phát triển nhanh chóng" },
            "Kaolin": { phonetic: "/ˈkeɪəlɪn/", meaning: "Cao lanh (Khoáng chất đất sét trong thủy sản)" },
            "Zeolite": { phonetic: "/ˈziːəlaɪt/", meaning: "Khoáng chất Zeolite (Hấp thụ độc tố, làm sạch nước)" }
        };

        const data = dictionary[word] || { phonetic: "/.../", meaning: "Từ vựng hệ thống" };

        // Tạo thành phần UI Popup
        const popup = document.createElement('div');
        popup.id = 'word-reader-popup';
        popup.className = 'absolute bg-slate-900 text-white p-4 rounded-xl shadow-2xl z-50 text-sm max-w-xs space-y-2 border border-slate-700 animate-fade-in';
        popup.innerHTML = `
            <div class="flex justify-between items-center space-x-4">
                <span class="font-bold text-amber-400 text-base">${word}</span>
                <button onclick="window.learnerCtrl.speak('${word}')" class="bg-indigo-600 hover:bg-indigo-700 p-1 rounded-full text-xs">🔊 Nghe</button>
            </div>
            <div class="text-xs text-slate-400 font-mono">${data.phonetic}</div>
            <div class="text-slate-200 border-t border-slate-700 pt-1.5">${data.meaning}</div>
        `;

        // Định vị vị trí popup ngay trên từ vừa click
        document.body.appendChild(popup);
        popup.style.left = `${event.pageX - (popup.offsetWidth / 2)}px`;
        popup.style.top = `${event.pageY - popup.offsetHeight - 12}px`;

        // Click ra ngoài để tắt popup
        setTimeout(() => {
            const closePopup = () => { popup.remove(); document.removeEventListener('click', closePopup); };
            document.addEventListener('click', closePopup);
        }, 100);
    }

    // MÀN HÌNH TỪ VỰNG - SƠ ĐỒ TƯ DUY (MINDMAP)
    startVocabView() {
        const container = document.getElementById('app-container');
        container.innerHTML = `
            <div class="space-y-6">
                <div class="flex justify-between items-center">
                    <button onclick="window.learnerCtrl.renderDashboard()" class="text-sm text-indigo-600 font-medium">← Quay lại màn hình chính</button>
                    <h2 class="text-xl font-bold text-slate-900">🧠 Sơ đồ tư duy Từ Vựng Hôm Nay</h2>
                </div>
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    <div class="lg:col-span-2 bg-white h-[500px] rounded-2xl border border-slate-200 shadow-sm relative overflow-hidden" id="mindmap-canvas"></div>
                    
                    <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
                        <div>
                            <div class="flex items-baseline space-x-2">
                                <div class="flex items-center space-x-3">
                                <h3 id="side-word" class="text-3xl font-bold text-indigo-600">Success</h3>
                                <button onclick="window.learnerCtrl.speak(document.getElementById('side-word').innerText)" class="bg-indigo-100 hover:bg-indigo-200 text-indigo-700 p-2 rounded-xl transition text-sm">
                                    🔊 Phát âm
                                </button>
                            </div>
                                <span id="side-phonetic" class="text-slate-400 text-sm font-mono">/səkˈses/</span>
                            </div>
                            <p id="side-meaning" class="text-lg font-medium text-slate-800 mt-1">Sự thành công</p>
                            
                            <div class="mt-6 bg-amber-50 rounded-xl p-4 border border-amber-200">
                                <span class="text-xs uppercase font-bold text-amber-700 tracking-wider block mb-1">💡 Câu chuyện hài cốt dễ thuộc:</span>
                                <p id="side-story" class="text-slate-700 text-sm leading-relaxed italic">"Muốn có 'Sự thành công' thì phải 'Sặc-cơm-sứt-vảy' nỗ lực bền bỉ."</p>
                            </div>
                        </div>

                        <div class="space-y-2 mt-6">
                            <span class="text-xs font-semibold text-slate-400 block text-center">Bạn nhớ từ này ở mức độ nào?</span>
                            <div class="grid grid-cols-3 gap-2">
                                <button onclick="window.db.updateProgress('v1', 'hard')" class="bg-rose-50 hover:bg-rose-100 text-rose-600 font-medium py-2 rounded-xl text-xs transition border border-rose-200">Quên mất</button>
                                <button onclick="window.db.updateProgress('v1', 'good')" class="bg-amber-50 hover:bg-amber-100 text-amber-600 font-medium py-2 rounded-xl text-xs transition border border-amber-200">Mơ hồ</button>
                                <button onclick="window.db.updateProgress('v1', 'easy')" class="bg-emerald-50 hover:bg-emerald-100 text-emerald-600 font-medium py-2 rounded-xl text-xs transition border border-emerald-200">Thuộc làu</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        this.drawMindmap();
    }

    drawMindmap() {
        // Khởi tạo thư viện Vis.js để vẽ đồ họa Mindmap động từ Database
        const container = document.getElementById('mindmap-canvas');
        const data = {
            nodes: new vis.DataSet([
                { id: 1, label: 'Success\n(Từ chính)', color: '#e0e7ff', font: { size: 18, bold: true } },
                { id: 2, label: 'Achievement\n(Đồng nghĩa)', color: '#ecfdf5' },
                { id: 3, label: 'Failure\n(Trái nghĩa)', color: '#fef2f2' },
                { id: 4, label: 'Successful\n(Hậu tố: Adjective)', color: '#fef3c7' },
                { id: 5, label: 'Succeed\n(Hậu tố: Verb)', color: '#fef3c7' }
            ]),
            edges: new vis.DataSet([
                { from: 1, to: 2, length: 150 }, { from: 1, to: 3, length: 150 },
                { from: 1, to: 4, length: 150 }, { from: 1, to: 5, length: 150 }
            ])
        };
        const options = { physics: { stabilization: true }, edges: { smooth: true, color: '#94a3b8' } };
        new vis.Network(container, data, options);
    }

    renderAuthZone() {
        const zone = document.getElementById('nav-auth-zone');
        const user = window.db.currentUser;
        if(user) {
            zone.innerHTML = `
                <span class="text-sm font-medium text-slate-600">👤 Chào, <b>${user.username}</b> (${user.role})</span>
                ${user.role === 'admin' ? `<button onclick="window.adminCtrl.renderAdminPanel()" class="bg-indigo-600 text-white px-3 py-1.5 rounded-xl text-xs font-semibold hover:bg-indigo-700 transition">Vào Admin</button>` : ''}
                <button onclick="window.db.logout(); window.learnerCtrl.renderDashboard();" class="text-xs text-rose-500 font-medium">Đăng xuất</button>
            `;
        } else {
            zone.innerHTML = `<button onclick="window.learnerCtrl.triggerLogin()" class="bg-slate-900 text-white px-4 py-2 rounded-xl text-xs font-semibold hover:bg-slate-800 transition">Đăng nhập hệ thống</button>`;
        }
    }

    triggerLogin() {
        const user = prompt("Nhập username (Nhập 'admin' để vào quyền quản trị):");
        const pass = prompt("Nhập password:");
    
        window.db.login(user, pass).then((loggedInUser) => {
            if (loggedInUser) {
                this.renderDashboard();
                showToast(`👋 Chào mừng ${loggedInUser.username} đã đăng nhập!`);
            } else {
                alert("❌ Sai tài khoản hoặc mật khẩu!");
            }
        });
    }
    speak(text) {
        if ('speechSynthesis' in window) {
            // Hủy các giọng đọc đang bị nghẽn trước đó
            window.speechSynthesis.cancel();

            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'en-US'; // Đặt ngôn ngữ chuẩn Mỹ (Có thể đổi thành 'en-GB' nếu muốn giọng Anh)
            utterance.rate = 0.9;     // Tốc độ đọc (0.9 giúp người học nghe rõ từng âm tiết hơn)
            utterance.pitch = 1.0;    // Cao độ giọng đọc

            // Chọn giọng đọc cao cấp (Premium) nếu trình duyệt có sẵn
            const voices = window.speechSynthesis.getVoices();
            const premiumVoice = voices.find(v => v.name.includes('Google US English') || v.name.includes('Samantha'));
            if (premiumVoice) utterance.voice = premiumVoice;

            window.speechSynthesis.speak(utterance);
        } else {
            alert("❌ Trình duyệt của bạn không hỗ trợ tính năng phát âm tự động.");
        }
    }
}