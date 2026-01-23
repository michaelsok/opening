document.addEventListener('DOMContentLoaded', () => {
    // State
    let currentUser = null;
    let selectedFile = null;

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

    // API URL (same host in production, localhost for dev)
    const API_BASE = '';

    // Transitions
    function showStep(step) {
        [authStep, dashboardStep, processingStep, successStep].forEach(s => s.classList.add('hidden'));
        step.classList.remove('hidden');
    }

    // --- Authentication ---
    connectBtn.addEventListener('click', async () => {
        const username = usernameInput.value.trim();
        if (!username) return;

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

            if (!response.ok) throw new Error('User not found');

            const data = await response.json();
            currentUser = data;

            // Setup Dashboard
            userDisplay.innerHTML = `
                <img src="${data.profile.avatar || 'https://www.chess.com/bundles/web/images/noavatar_l.84a92b24.gif'}" alt="Avatar">
                <div class="user-info">
                    <h3>${data.profile.name || data.username}</h3>
                    <p>${data.profile.location || 'Chess Enthusiast'}</p>
                </div>
            `;

            showStep(dashboardStep);
        } catch (err) {
            authError.classList.remove('hidden');
        } finally {
            connectBtn.disabled = false;
            connectBtn.innerHTML = '<span>Connect with Chess.com</span><i data-lucide="chevron-right"></i>';
            lucide.createIcons();
        }
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
            categoryLabels.innerHTML = data.categories.map(cat => `
                <span style="background: rgba(129, 140, 248, 0.2); border: 1px solid var(--primary); padding: 4px 12px; border-radius: 20px; font-size: 0.75rem;">
                    ${cat}
                </span>
            `).join('');

            showStep(successStep);
        } catch (err) {
            console.error(err);
            uploadError.textContent = err.message;
            uploadError.classList.remove('hidden');
            showStep(dashboardStep);
        }
    });
});
