/**
 * MelodyAI - Frontend Application & API Connector Engine
 * Connects UI inputs to FastAPI backend, sends composition requests,
 * handles response audio & MIDI URLs, manages error states, shows toast notifications,
 * and animates the audio visualizer canvas.
 */

document.addEventListener('DOMContentLoaded', () => {
    // UI Form Elements
    const tempSlider = document.getElementById('tempSlider');
    const tempValueDisplay = document.getElementById('tempValueDisplay');
    const genreSelect = document.getElementById('genreSelect');
    const lengthSelect = document.getElementById('lengthSelect');
    const generateBtn = document.getElementById('generateBtn');
    const btnSpinner = document.getElementById('btnSpinner');
    const loadingOverlay = document.getElementById('loadingOverlay');
    const loadingText = document.getElementById('loadingText');
    const statusIndicator = document.getElementById('statusIndicator');
    const toastContainer = document.getElementById('toastContainer');

    // Audio Player Elements
    const audioPlayer = document.getElementById('audioPlayer');
    const playPauseBtn = document.getElementById('playPauseBtn');
    const playIcon = document.getElementById('playIcon');
    const rewindBtn = document.getElementById('rewindBtn');
    const forwardBtn = document.getElementById('forwardBtn');
    const progressContainer = document.getElementById('progressContainer');
    const progressBar = document.getElementById('progressBar');
    const currentTimeEl = document.getElementById('currentTime');
    const durationTimeEl = document.getElementById('durationTime');

    // Metadata & Download Elements
    const trackTitle = document.getElementById('trackTitle');
    const tagGenre = document.getElementById('tagGenre');
    const tagTemp = document.getElementById('tagTemp');
    const tagNotes = document.getElementById('tagNotes');
    const downloadMidiBtn = document.getElementById('downloadMidiBtn');
    const downloadWavBtn = document.getElementById('downloadWavBtn');

    // Waveform Canvas Elements
    const canvas = document.getElementById('waveformCanvas');
    const ctx = canvas.getContext('2d');
    let animationFrameId;

    // Responsive Canvas Resizing
    function resizeCanvas() {
        canvas.width = canvas.parentElement.clientWidth;
        canvas.height = canvas.parentElement.clientHeight;
    }
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // 1. Temperature Slider Display Update
    tempSlider.addEventListener('input', (e) => {
        const val = parseFloat(e.target.value).toFixed(2);
        tempValueDisplay.textContent = val;
    });

    // 2. Audio Player Logic
    let isPlaying = false;

    function togglePlay() {
        if (audioPlayer.paused) {
            audioPlayer.play().then(() => {
                isPlaying = true;
                playIcon.className = 'fa-solid fa-pause';
                startWaveformAnimation();
            }).catch(err => {
                console.warn('Playback deferred:', err);
            });
        } else {
            audioPlayer.pause();
            isPlaying = false;
            playIcon.className = 'fa-solid fa-play';
            stopWaveformAnimation();
        }
    }

    playPauseBtn.addEventListener('click', togglePlay);

    rewindBtn.addEventListener('click', () => {
        audioPlayer.currentTime = Math.max(0, audioPlayer.currentTime - 5);
    });

    forwardBtn.addEventListener('click', () => {
        audioPlayer.currentTime = Math.min(audioPlayer.duration || 0, audioPlayer.currentTime + 5);
    });

    audioPlayer.addEventListener('timeupdate', () => {
        if (audioPlayer.duration) {
            const pct = (audioPlayer.currentTime / audioPlayer.duration) * 100;
            progressBar.style.width = `${pct}%`;
            currentTimeEl.textContent = formatTime(audioPlayer.currentTime);
            durationTimeEl.textContent = formatTime(audioPlayer.duration);
        }
    });

    audioPlayer.addEventListener('ended', () => {
        isPlaying = false;
        playIcon.className = 'fa-solid fa-play';
        progressBar.style.width = '0%';
        stopWaveformAnimation();
    });

    progressContainer.addEventListener('click', (e) => {
        const rect = progressContainer.getBoundingClientRect();
        const clickX = e.clientX - rect.left;
        if (audioPlayer.duration) {
            audioPlayer.currentTime = (clickX / rect.width) * audioPlayer.duration;
        }
    });

    function formatTime(seconds) {
        if (isNaN(seconds)) return "00:00";
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }

    // 3. Animated Canvas Waveform Visualizer
    function drawWaveform() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        const numBars = 52;
        const barWidth = (canvas.width / numBars) - 3;
        const centerY = canvas.height / 2;

        for (let i = 0; i < numBars; i++) {
            let height;
            if (isPlaying) {
                const time = Date.now() * 0.006;
                height = Math.sin(time + i * 0.25) * (canvas.height * 0.35) + (canvas.height * 0.4);
                height += Math.random() * 6;
            } else {
                height = Math.sin(i * 0.3) * 10 + 18;
            }

            const x = i * (barWidth + 3);
            const y = centerY - height / 2;

            const gradient = ctx.createLinearGradient(0, y, 0, y + height);
            gradient.addColorStop(0, '#8B5CF6');
            gradient.addColorStop(0.5, '#06B6D4');
            gradient.addColorStop(1, '#EC4899');

            ctx.fillStyle = gradient;
            ctx.beginPath();
            ctx.roundRect(x, y, barWidth, height, 4);
            ctx.fill();
        }

        if (isPlaying) {
            animationFrameId = requestAnimationFrame(drawWaveform);
        }
    }

    function startWaveformAnimation() {
        if (!animationFrameId) {
            drawWaveform();
        }
    }

    function stopWaveformAnimation() {
        cancelAnimationFrame(animationFrameId);
        animationFrameId = null;
        drawWaveform();
    }

    drawWaveform();

    // 4. Toast Notification Utility
    function showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        const icon = type === 'success' ? 'fa-circle-check' : 'fa-circle-exclamation';
        toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${message}</span>`;
        
        toastContainer.appendChild(toast);
        
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            setTimeout(() => toast.remove(), 400);
        }, 4000);
    }

    // 5. Connect Frontend to Backend API Request
    generateBtn.addEventListener('click', async () => {
        const genre = genreSelect.value;
        const length = parseInt(lengthSelect.value);
        const temperature = parseFloat(tempSlider.value);

        // Show 7. Loading Indicator & Overlay
        loadingOverlay.classList.remove('hidden');
        btnSpinner.classList.remove('hidden');
        generateBtn.disabled = true;
        loadingText.textContent = `Deep LSTM neural net is composing ${length}-note ${genre} track (&tau; = ${temperature})...`;
        statusIndicator.innerHTML = '<span class="status-dot yellow"></span> Generating...';

        if (isPlaying) {
            togglePlay();
        }

        try {
            // Determine API base URL dynamically
            let apiEndpoint = '/api/generate';
            if (window.location.protocol === 'file:' || (window.location.port && window.location.port !== '8000')) {
                apiEndpoint = 'http://127.0.0.1:8000/api/generate';
            }

            let response;
            try {
                response = await fetch(apiEndpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ genre, length, temperature })
                });
            } catch (networkErr) {
                // If primary endpoint failed and wasn't explicit 8000, retry explicitly on port 8000
                if (apiEndpoint !== 'http://127.0.0.1:8000/api/generate') {
                    response = await fetch('http://127.0.0.1:8000/api/generate', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ genre, length, temperature })
                    });
                } else {
                    throw networkErr;
                }
            }

            if (!response.ok) {
                const errData = await response.json().catch(() => ({}));
                throw new Error(errData.detail || `Server returned HTTP ${response.status}`);
            }

            const data = await response.json();

            if (!data.success) {
                throw new Error(data.message || 'Generation failed');
            }

            // Determine base URL prefix for returned static files
            const serverBase = apiEndpoint.startsWith('http') ? 'http://127.0.0.1:8000' : '';
            const wavUrl = `${serverBase}${data.wav_url}?t=${Date.now()}`;
            const midiUrl = `${serverBase}${data.midi_url}?t=${Date.now()}`;

            // Update Metadata Tags
            trackTitle.textContent = `AI ${data.genre.toUpperCase()} #${data.filename.slice(-5)}`;
            tagGenre.textContent = data.genre.charAt(0).toUpperCase() + data.genre.slice(1);
            tagTemp.textContent = `Temp: ${data.temperature.toFixed(2)}`;
            tagNotes.textContent = `${data.notes_count} Notes`;

            // Update Player Audio Source & Download Links
            audioPlayer.src = wavUrl;
            downloadWavBtn.href = wavUrl;
            downloadMidiBtn.href = midiUrl;
            downloadWavBtn.setAttribute('download', `${data.filename}.wav`);
            downloadMidiBtn.setAttribute('download', `${data.filename}.mid`);

            // Show Success Notification
            showToast(`Composition created successfully in ${data.generation_time_seconds}s!`, 'success');

            // Auto Play
            togglePlay();

        } catch (error) {
            console.error('Music Generation Error:', error);
            
            // Check if network error (backend server not running)
            if (error.message.includes('Failed to fetch') || error.name === 'TypeError') {
                showToast('Backend server not connected. Starting server with: python api/app.py', 'error');
                
                // Fallback to locally available generated composition
                const localWav = '../output/ai_composition_temp_0.9.wav';
                const localMidi = '../output/ai_composition_temp_0.9.mid';
                
                audioPlayer.src = `${localWav}?t=${Date.now()}`;
                downloadWavBtn.href = localWav;
                downloadMidiBtn.href = localMidi;
                
                trackTitle.textContent = `AI ${genre.toUpperCase()} (Demo Preview)`;
                tagGenre.textContent = genre.charAt(0).toUpperCase() + genre.slice(1);
                tagTemp.textContent = `Temp: ${temperature.toFixed(2)}`;
                tagNotes.textContent = `${length} Notes`;
                
                togglePlay();
            } else {
                showToast(`Generation Error: ${error.message}`, 'error');
            }
            statusIndicator.innerHTML = '<span class="status-dot red"></span> Connection Error';
        } finally {
            // Hide Loading Overlay & Restore Button
            loadingOverlay.classList.add('hidden');
            btnSpinner.classList.add('hidden');
            generateBtn.disabled = false;
            statusIndicator.innerHTML = '<span class="status-dot green"></span> Ready';
        }
    });
});
