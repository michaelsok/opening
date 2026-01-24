document.addEventListener('DOMContentLoaded', () => {
    // State
    let currentUser = null;
    let selectedFile = null;
    let selectedColor = 'white';

    // Elements
    const authStep = document.getElementById('auth-step');
    const dashboardStep = document.getElementById('dashboard-step');
    const processingStep = document.getElementById('processing-step');
    const successStep = document.getElementById('success-step');

    const usernameInput = document.getElementById('username');
    const connectBtn = document.getElementById('connect-btn');
    const authError = document.getElementById('auth-error');

    const uploadZone = document.getElementById('upload-zone');
    const fileInput = document.getElementById('file-input');
    const fileInfo = document.getElementById('file-info');
    const filenameDisplay = document.getElementById('filename');
    const removeFileBtn = document.getElementById('remove-file');
    const analyzeBtn = document.getElementById('analyze-btn');
    const uploadError = document.getElementById('upload-error');

    const userDisplay = document.getElementById('user-display');
    const categoryLabels = document.getElementById('category-labels');

    const colorWhiteBtn = document.getElementById('color-white');
    const colorBlackBtn = document.getElementById('color-black');
    const resetBtn = document.getElementById('reset-btn');

    // API URL (same host in production, localhost for dev)
    const API_BASE = '';

    // Transitions
    function showStep(step) {
        [authStep, dashboardStep, processingStep, successStep].forEach(s => s.classList.add('hidden'));
        step.classList.remove('hidden');
    }

    // --- Authentication ---
    connectBtn.addEventListener('click', async () => {
        let username = usernameInput.value.trim();
        if (!username) return;

        // Auto-extract from URL if user pasted a link
        if (username.includes('chess.com/member/')) {
            username = username.split('chess.com/member/')[1].split('/')[0].split('?')[0];
        } else if (username.includes('chess.com/player/')) {
            username = username.split('chess.com/player/')[1].split('/')[0].split('?')[0];
        }

        connectBtn.disabled = true;
        connectBtn.innerHTML = '<div class="loader"></div>';
        authError.classList.add('hidden');

        try {
            const formData = new FormData();
            formData.append('username', username);

            const response = await fetch(`${API_BASE}/auth/verify`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Connection failed');
            }

            const data = await response.json();
            currentUser = data;

            // Setup Dashboard
            userDisplay.innerHTML = '';

            const avatarImg = document.createElement('img');
            const avatarUrl = data.profile.avatar;

            // Handle profile picture with fallback to chess piece icon
            if (avatarUrl) {
                avatarImg.src = avatarUrl;
                avatarImg.onerror = () => {
                    avatarImg.classList.add('hidden');
                    const iconP = document.createElement('div');
                    iconP.className = 'avatar-placeholder';
                    iconP.textContent = '♟️';
                    userDisplay.insertBefore(iconP, userDisplay.firstChild);
                };
            } else {
                const iconP = document.createElement('div');
                iconP.className = 'avatar-placeholder';
                iconP.textContent = '♟️';
                userDisplay.appendChild(iconP);
                avatarImg.classList.add('hidden');
            }
            avatarImg.alt = 'Avatar';

            const infoDiv = document.createElement('div');
            infoDiv.className = 'user-info';

            const nameH3 = document.createElement('h3');
            nameH3.textContent = data.profile.name || data.username;

            const locP = document.createElement('p');
            locP.textContent = data.profile.location || 'Chess Enthusiast';

            infoDiv.appendChild(nameH3);
            infoDiv.appendChild(locP);
            userDisplay.appendChild(avatarImg);
            userDisplay.appendChild(infoDiv);

            showStep(dashboardStep);
        } catch (err) {
            authError.textContent = err.message;
            authError.classList.remove('hidden');
        } finally {
            connectBtn.disabled = false;
            connectBtn.innerHTML = '<span>Connect with Chess.com</span><i data-lucide="chevron-right"></i>';
            lucide.createIcons();
        }
    });

    // --- Color Toggle ---
    [colorWhiteBtn, colorBlackBtn].forEach(btn => {
        btn.addEventListener('click', () => {
            colorWhiteBtn.classList.remove('active');
            colorBlackBtn.classList.remove('active');
            btn.classList.add('active');
            selectedColor = btn.dataset.color;
        });
    });

    // --- Upload Logic ---
    uploadZone.addEventListener('click', () => fileInput.click());

    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.classList.add('dragging');
    });

    uploadZone.addEventListener('dragleave', () => {
        uploadZone.classList.remove('dragging');
    });

    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('dragging');
        handleFiles(e.dataTransfer.files);
    });

    fileInput.addEventListener('change', (e) => {
        handleFiles(e.target.files);
    });

    function handleFiles(files) {
        if (files.length === 0) return;
        const file = files[0];

        if (!file.name.endsWith('.pgn')) {
            alert('Please upload a .pgn file');
            return;
        }

        selectedFile = file;
        filenameDisplay.textContent = file.name;
        fileInfo.classList.remove('hidden');
        uploadZone.classList.add('hidden');
        analyzeBtn.disabled = false;
    }

    removeFileBtn.addEventListener('click', () => {
        selectedFile = null;
        fileInfo.classList.add('hidden');
        uploadZone.classList.remove('hidden');
        analyzeBtn.disabled = true;
        fileInput.value = '';
    });

    // --- Analysis Trigger ---
    analyzeBtn.addEventListener('click', async () => {
        if (!selectedFile || !currentUser) return;

        showStep(processingStep);
        uploadError.classList.add('hidden');

        try {
            const formData = new FormData();
            formData.append('username', currentUser.username);
            formData.append('file', selectedFile);
            formData.append('color', selectedColor);

            const response = await fetch(`${API_BASE}/repertoire/upload`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || 'Upload failed');
            }

            const data = await response.json();

            // Show Success
            categoryLabels.innerHTML = '';
            data.categories.forEach(cat => {
                const badge = document.createElement('span');
                badge.style.background = 'rgba(129, 140, 248, 0.2)';
                badge.style.border = '1px solid var(--primary)';
                badge.style.padding = '4px 12px';
                badge.style.borderRadius = '20px';
                badge.style.fontSize = '0.75rem';
                badge.textContent = cat;
                categoryLabels.appendChild(badge);
            });

            showStep(successStep);
        } catch (err) {
            console.error(err);
            uploadError.textContent = err.message;
            uploadError.classList.remove('hidden');
            showStep(dashboardStep);
        }
    });

    // --- Reset Flow ---
    resetBtn.addEventListener('click', () => {
        selectedFile = null;
        fileInput.value = '';
        fileInfo.classList.add('hidden');
        uploadZone.classList.remove('hidden');
        analyzeBtn.disabled = true;
        analysisResult.classList.add('hidden');
        showStep(dashboardStep);
    });

    // --- Analysis Filters & Trigger ---
    const runAnalysisBtn = document.getElementById('run-analysis-btn');
    const analysisYear = document.getElementById('analysis-year');
    const analysisMonth = document.getElementById('analysis-month');
    const analysisResult = document.getElementById('analysis-result');
    const analysisInfo = document.getElementById('analysis-info');
    const viewReportLink = document.getElementById('view-report-link');

    // Set default month to current
    const now = new Date();
    analysisYear.value = now.getFullYear().toString();
    analysisMonth.value = (now.getMonth() + 1).toString().padStart(2, '0');

    let analysisColor = ''; // empty string means "All Games"

    document.querySelectorAll('[data-analysis-color]').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('[data-analysis-color]').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            analysisColor = btn.dataset.analysisColor;
        });
    });

    runAnalysisBtn.addEventListener('click', async () => {
        if (!currentUser) return;

        runAnalysisBtn.disabled = true;
        runAnalysisBtn.innerHTML = '<div class="loader"></div>';
        analysisResult.classList.add('hidden');

        try {
            const formData = new FormData();
            formData.append('username', currentUser.username);
            formData.append('year', analysisYear.value);
            formData.append('month', analysisMonth.value);
            if (analysisColor) {
                formData.append('color', analysisColor);
            }

            const response = await fetch(`${API_BASE}/analysis/run`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || 'Analysis failed');
            }

            const data = await response.json();

            if (data.status === 'empty') {
                analysisInfo.textContent = data.message;
                analysisInfo.style.color = 'var(--text-muted)';
                viewReportLink.classList.add('hidden');
            } else {
                analysisInfo.textContent = `Generated report for ${data.game_count} games!`;
                analysisInfo.style.color = '#10b981';
                viewReportLink.href = data.report_url;
                viewReportLink.classList.remove('hidden');
            }

            analysisResult.classList.remove('hidden');
        } catch (err) {
            console.error(err);
            alert(err.message);
        } finally {
            runAnalysisBtn.disabled = false;
            runAnalysisBtn.innerHTML = '<span>Find Games & Divergences</span><i data-lucide="scan-search"></i>';
            lucide.createIcons();
        }
    });
});
