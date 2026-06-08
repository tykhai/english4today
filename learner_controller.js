class LearnerController {
    renderDashboard() {
        this.renderAuthZone();
        const container = document.getElementById('app-container');
        const user = window.db.currentUser;

        // GIAO DIỆN KHI CHƯA ĐĂNG NHẬP
        if (!user) {
            container.innerHTML = `
                <div class="text-center py-20 bg-white rounded-3xl border border-slate-200 shadow-sm max-w-xl mx-auto space-y-4">
                    <div class="text-5xl">🔐</div>
                    <h2 class="text-2xl font-bold text-slate-800">Vui lòng đăng nhập hệ thống</h2>
                    <p class="text-slate-500 text-sm">Bạn cần đăng nhập tài khoản để lưu tiến trình học tập đồng bộ xuyên thiết bị.</p>
                    <div class="flex justify-center space-x-3 pt-2">
                        <button onclick="window.learnerCtrl.triggerLogin()" class="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold px-6 py-2.5 rounded-xl transition">Đăng Nhập</button>
                        <button onclick="window.learnerCtrl.triggerRegister()" class="bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold px-6 py-2.5 rounded-xl transition">Đăng Ký Tài Khoản</button>
                    </div>
                </div>
            `;
            return;
        }

        // GIAO DIỆN KHI ĐÃ ĐĂNG NHẬP (Phân quyền cấu duyệt từ DB)
        container.innerHTML = `
            <div class="space-y-8">
                <div class="bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 rounded-3xl p-6 text-white shadow-lg">
                    <h2 class="text-2xl font-bold">Chào mừng bạn trở lại học tập! 🔥</h2>
                    <p class="text-white/80 text-sm mt-1">Tài khoản: <b class="text-amber-300">${user.username}</b> | Vai trò: <span class="capitalize font-bold">${user.role}</span></p>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                    ${user.allow_reading_part || user.role === 'admin' ? `
                    <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition cursor-pointer" onclick="window.learnerCtrl.startReadingView('B')">
                        <div class="text-3xl mb-2">📚</div>
                        <h3 class="font-bold text-lg text-slate-900">Luyện Bài Đọc Theo Cấp Độ</h3>
                        <p class="text-slate-500 text-sm mt-1">Học ngữ pháp, tra cứu trực tiếp từ vựng ngay trong ngữ cảnh.</p>
                    </div>
                    ` : `
                    <div class="bg-slate-100 p-6 rounded-2xl border border-slate-200 opacity-60 cursor-not-allowed">
                        <div class="text-3xl mb-2">🔒</div>
                        <h3 class="font-bold text-lg text-slate-400">Luyện Bài Đọc (Khóa)</h3>
                        <p class="text-slate-400 text-sm mt-1">Tài khoản của bạn chưa được cấp quyền học phần này. Hãy liên hệ Admin.</p>
                    </div>
                    `}

                    ${user.allow_vocab_part || user.role === 'admin' ? `
                    <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition cursor-pointer" onclick="window.learnerCtrl.startVocabView()">
                        <div class="text-3xl mb-2">🧠</div>
                        <h3 class="font-bold text-lg text-slate-900">Từ Vựng & Sơ Đồ Tư Duy</h3>
                        <p class="text-slate-500 text-sm mt-1">Mẹo học hài hước thông qua cốt truyện, sơ đồ tư duy rực rỡ.</p>
                    </div>
                    ` : `
                    <div class="bg-slate-100 p-6 rounded-2xl border border-slate-200 opacity-60 cursor-not-allowed">
                        <div class="text-3xl mb-2">🔒</div>
                        <h3 class="font-bold text-lg text-slate-400">Từ Vựng & Sơ Đồ (Khóa)</h3>
                        <p class="text-slate-400 text-sm mt-1">Tài khoản của bạn chưa được cấp quyền học phần này. Hãy liên hệ Admin.</p>
                    </div>
                    `}

                    ${user.role === 'admin' ? `
                    <div class="bg-amber-50 p-6 rounded-2xl border-2 border-dashed border-amber-300 shadow-sm hover:shadow-md transition cursor-pointer" onclick="window.adminCtrl.renderAdminPanel()">
                        <div class="text-3xl mb-2">⚙️</div>
                        <h3 class="font-bold text-lg text-amber-800">Bảng Quản Trị Hệ Thống</h3>
                        <p class="text-amber-600 text-sm mt-1">Quản lý, cấp quyền user, xem danh sách học viên và nạp bài học mới.</p>
                    </div>
                    ` : ''}
                </div>
            </div>
        `;
    }

    async startReadingView(level) {
        const lessons = await window.db.getReadingLessons(level);
        if (lessons.length === 0) {
            alert("Hiện tại chưa có bài đọc nào cấp độ này trong Database. Hãy vào Admin nạp bài trước!");
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
                    <div class="font-reading text-xl text-slate-700 leading-relaxed space-y-4">
                        ${this.highlightContent(lesson.content)}
                    </div>
                </div>
                <div class="bg-slate-900 text-slate-100 p-6 rounded-2xl shadow-sm flex flex-col justify-between">
                    <div>
                        <h3 class="text-amber-400 font-bold text-lg mb-4 flex items-center">💡 Cấu trúc Ngữ Pháp</h3>
                        <div class="space-y-4">
                            <h4 class="font-bold text-white text-base">${lesson.grammar_points[0]?.structures || 'N/A'}</h4>
                            <p class="text-sm text-slate-400 leading-relaxed">${lesson.grammar_points[0]?.explanation || ''}</p>
                            <div class="bg-white/5 border-l-2 border-amber-400 p-3 rounded-r-xl italic text-sm text-slate-300">
                                "${lesson.grammar_points[0]?.examples[0] || ''}"
                            </div>
                        </div>
                    </div>
                    <div class="mt-8 border-t border-white/10 pt-4 text-xs text-slate-500">Mẹo: Click trực tiếp vào các từ vựng màu vàng trong bài để xem nghĩa và nghe đọc.</div>
                </div>
            </div>
        `;
    }

    highlightContent(content) {
        return content.replace(/(Kaolin|Zeolite|expanding|intelligence|aquaculture)/gi, 
            `<span class="bg-amber-100 text-amber-900 font-bold px-1 rounded cursor-pointer border-b-2 border-amber-400 hover:bg-amber-200 transition" 
                   onclick="window.learnerCtrl.showWordPopup(event, '$1')">$1</span>`);
    }

    showWordPopup(event, word) {
        const oldPopup = document.getElementById('word-reader-popup');
        if (oldPopup) oldPopup.remove();

        const dictionary = {
            "expanding": { phonetic: "/ɪkˈspændɪŋ/", meaning: "Mở rộng, phát triển nhanh chóng" },
            "kaolin": { phonetic: "/ˈkeɪəlɪn/", meaning: "Cao lanh (Khoáng chất đất sét trong thủy sản)" },
            "zeolite": { phonetic: "/ˈziːəlaɪt/", meaning: "Khoáng chất Zeolite (Hấp thụ độc tố, làm sạch nước)" },
            "intelligence": { phonetic: "/ɪnˈtelɪdʒəns/", meaning: "Trí tuệ, thông minh" },
            "aquaculture": { phonetic: "/ˈækwəkʌltʃə(r)/", meaning: "Ngành nuôi trồng thủy sản" }
        };

        const data = dictionary[word.toLowerCase()] || { phonetic: "/.../", meaning: "Từ vựng hệ thống bài đọc" };

        const popup = document.createElement('div');
        popup.id = 'word-reader-popup';
        popup.className = 'absolute bg-slate-900 text-white p-4 rounded-xl shadow-2xl z-50 text-sm max-w-xs space-y-2 border border-slate-700';
        popup.innerHTML = `
            <div class="flex justify-between items-center space-x-4">
                <span class="font-bold text-amber-400 text-base">${word}</span>
                <button onclick="window.learnerCtrl.speak('${word}')" class="bg-indigo-600 hover:bg-indigo-700 px-2 py-1 rounded-lg text-xs flex items-center">🔊 Nghe</button>
            </div>
            <div class="text-xs text-slate-400 font-mono">${data.phonetic}</div>
            <div class="text-slate-200 border-t border-slate-700 pt-1.5">${data.meaning}</div>
        `;

        document.body.appendChild(popup);
        popup.style.left = `${event.pageX - (popup.offsetWidth / 2)}px`;
        popup.style.top = `${event.pageY - popup.offsetHeight - 12}px`;

        setTimeout(() => {
            const closePopup = () => { popup.remove(); document.removeEventListener('click', closePopup); };
            document.addEventListener('click', closePopup);
        }, 100);
    }

    startVocabView() {
        const container = document.getElementById('app-container');
        container.innerHTML = `
            <div class="space-y-6">
                <div class="flex justify-between items-center">
                    <button onclick="window.learnerCtrl.renderDashboard()" class="text-sm text-indigo-600 font-medium">← Quay lại</button>
                    <h2 class="text-xl font-bold text-slate-900">🧠 Sơ đồ tư duy Từ Vựng Hôm Nay</h2>
                </div>
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    <div class="lg:col-span-2 bg-white h-[500px] rounded-2xl border border-slate-200 shadow-sm" id="mindmap-canvas"></div>
                    
                    <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
                        <div>
                            <div class="flex items-center justify-between">
                                <h3 id="side-word" class="text-3xl font-bold text-indigo-600">Success</h3>
                                <button onclick="window.learnerCtrl.speak(document.getElementById('side-word').innerText)" class="bg-indigo-100 hover:bg-indigo-200 text-indigo-700 px-3 py-1.5 rounded-xl transition text-sm font-medium">🔊 Nghe phát âm</button>
                            </div>
                            <span id="side-phonetic" class="text-slate-400 text-sm font-mono block mt-1">/səkˈses/</span>
                            <p id="side-meaning" class="text-lg font-medium text-slate-800 mt-1">Sự thành công</p>
                            
                            <div class="mt-6 bg-amber-50 rounded-xl p-4 border border-amber-200">
                                <span class="text-xs uppercase font-bold text-amber-700 tracking-wider block mb-1">💡 Mẹo học cốt truyện hài hước:</span>
                                <p id="side-story" class="text-slate-700 text-sm leading-relaxed italic">"Muốn có 'Sự thành công' thì phải 'Sặc-cơm-sứt-vảy' nỗ lực bền bỉ."</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        this.drawMindmap();
    }

    drawMindmap() {
        const container = document.getElementById('mindmap-canvas');
        const data = {
            nodes: new vis.DataSet([
                { id: 1, label: 'Success\n(Từ chính)', color: '#e0e7ff', font: { size: 18, bold: true } },
                { id: 2, label: 'Achievement\n(Đồng nghĩa)', color: '#ecfdf5' },
                { id: 3, label: 'Failure\n(Trái nghĩa)', color: '#fef2f2' },
                { id: 4, label: 'Successful\n(Tính từ)', color: '#fef3c7' }
            ]),
            edges: new vis.DataSet([
                { from: 1, to: 2 }, { from: 1, to: 3 }, { from: 1, to: 4 }
            ])
        };
        new vis.Network(container, data, { edges: { smooth: true, color: '#94a3b8' } });
    }

    renderAuthZone() {
        const zone = document.getElementById('nav-auth-zone');
        const user = window.db.currentUser;
        if(user) {
            zone.innerHTML = `
                <span class="text-sm font-medium text-slate-600">👤 <b>${user.username}</b></span>
                <button onclick="window.db.logout(); window.learnerCtrl.renderDashboard();" class="text-xs text-rose-500 font-medium ml-2">Đăng xuất</button>
            `;
        } else {
            zone.innerHTML = `
                <button onclick="window.learnerCtrl.triggerLogin()" class="bg-slate-900 text-white px-4 py-2 rounded-xl text-xs font-semibold hover:bg-slate-800 transition">Đăng nhập</button>
                <button onclick="window.learnerCtrl.triggerRegister()" class="bg-slate-100 text-slate-700 px-4 py-2 rounded-xl text-xs font-semibold hover:bg-slate-200 transition ml-2">Đăng ký</button>
            `;
        }
    }

    async triggerLogin() {
        const user = prompt("Nhập Username:");
        const pass = prompt("Nhập Password:");
        if(!user || !pass) return;
        
        const loggedInUser = await window.db.login(user, pass);
        if (loggedInUser) {
            this.renderDashboard();
            showToast(`👋 Đăng nhập thành công!`);
        } else {
            alert("❌ Tài khoản hoặc mật khẩu không chính xác trên Cloud!");
        }
    }

    async triggerRegister() {
        const user = prompt("Tạo tên tài khoản mới:");
        const pass = prompt("Tạo mật khẩu:");
        if(!user || !pass) return;

        const success = await window.db.register(user, pass);
        if(success) {
            alert("🎉 Đăng ký thành công! Hãy bấm Đăng nhập.");
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