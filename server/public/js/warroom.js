(function() {
    const CONFIG = {
        apiBase: '/api/v1/admin/threat',
        updateInterval: 30000
    };

    const elements = {
        statusBadge: document.getElementById('statusBadge'),
        valuationBadge: document.getElementById('valuationBadge'),
        threatLevel: document.getElementById('threatLevel'),
        activeQuarantines: document.getElementById('activeQuarantines'),
        recentAlerts: document.getElementById('recentAlerts'),
        valuationRisk: document.getElementById('valuationRisk'),
        threatTrend: document.getElementById('threatTrend'),
        meterFill: document.getElementById('meterFill'),
        meterContainer: document.querySelector('.meter-container'),
        threatsBody: document.getElementById('threatsBody'),
        alertFeed: document.getElementById('alertFeed'),
        heatmapGrid: document.getElementById('heatmapGrid'),
        heatmapStats: document.getElementById('heatmapStats'),
        timestamp: document.getElementById('timestamp')
    };

    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = '/login.html?redirect=warroom';
        return;
    }

    function initMatrix() {
        const canvas = document.getElementById('matrixCanvas');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        
        function resize() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }
        
        resize();
        window.addEventListener('resize', resize);

        const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789@#$%^&*()';
        const fontSize = 10;
        const columns = canvas.width / fontSize;
        const drops = new Array(Math.floor(columns)).fill(1);

        function draw() {
            ctx.fillStyle = 'rgba(0, 0, 0, 0.04)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#0F0';
            ctx.font = fontSize + 'px monospace';

            for (let i = 0; i < drops.length; i++) {
                const text = chars[Math.floor(Math.random() * chars.length)];
                ctx.fillText(text, i * fontSize, drops[i] * fontSize);
                if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
                    drops[i] = 0;
                }
                drops[i]++;
            }
            requestAnimationFrame(draw);
        }
        draw();
    }

    async function fetchData() {
        try {
            const response = await fetch(CONFIG.apiBase + '/posture', {
                headers: { 'Authorization': 'Bearer ' + token }
            });
            if (!response.ok) throw new Error('Fetch failed');
            const result = await response.json();
            if (result && result.success) {
                updateDashboard(result.data);
            }
        } catch (error) {
            console.error('Failed to fetch data:', error);
        }
    }

    function updateDashboard(data) {
        if (elements.statusBadge) {
            elements.statusBadge.textContent = data.status || 'UNKNOWN';
        }
        if (elements.threatLevel) {
            elements.threatLevel.textContent = data.threatLevel || '0';
        }
        if (elements.activeQuarantines) {
            elements.activeQuarantines.textContent = (data.metrics && data.metrics.activeQuarantines) || 0;
        }
        if (elements.recentAlerts) {
            elements.recentAlerts.textContent = (data.metrics && data.metrics.recentAlerts) || 0;
        }
        if (elements.valuationRisk) {
            elements.valuationRisk.textContent = data.valuationRisk || 'LOW';
        }
        if (elements.threatTrend) {
            elements.threatTrend.textContent = (data.prediction && data.prediction.trend) || 'STABLE';
        }
        if (elements.meterFill && data.threatLevel !== undefined) {
            elements.meterFill.style.width = data.threatLevel + '%';
            elements.meterFill.className = 'meter-fill';
            if (data.status) {
                elements.meterFill.classList.add(data.status.toLowerCase());
            }
        }
        if (elements.meterContainer && data.threatLevel !== undefined) {
            elements.meterContainer.setAttribute('aria-valuenow', data.threatLevel);
        }
        if (data.topThreats) {
            updateThreatsTable(data.topThreats);
        }
        if (elements.timestamp) {
            elements.timestamp.textContent = 'Last Update: ' + new Date().toLocaleString();
        }
    }

    function updateThreatsTable(threats) {
        if (!elements.threatsBody) return;
        elements.threatsBody.innerHTML = '';
        if (!threats || threats.length === 0) {
            elements.threatsBody.innerHTML = '<tr><td colspan="4" class="loading-message">No threats detected</td></tr>';
            return;
        }
        threats.slice(0, 10).forEach(function(threat) {
            var row = elements.threatsBody.insertRow();
            row.insertCell(0).textContent = threat.type || 'UNKNOWN';
            row.insertCell(1).textContent = threat.count || 0;
            row.insertCell(2).textContent = threat.severity || 'INFO';
            row.insertCell(3).textContent = threat.lastSeen ? new Date(threat.lastSeen).toLocaleString() : 'N/A';
        });
    }

    initMatrix();
    fetchData();
    setInterval(fetchData, CONFIG.updateInterval);
})();
