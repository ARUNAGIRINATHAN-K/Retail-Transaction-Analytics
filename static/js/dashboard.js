document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const ngrokInput = document.getElementById('ngrok-url');
    const connectBtn = document.getElementById('connect-btn');
    const statusInd = document.getElementById('status-indicator');
    const debugLog = document.getElementById('debug-log');

    const uploadSection = document.getElementById('upload-section');
    const kpiSection = document.getElementById('kpi-section');
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const fileInfo = document.getElementById('file-info');

    const resultsSection = document.getElementById('results-section');
    const salesChartCanvas = document.getElementById('salesChart');
    const topProductsCanvas = document.getElementById('topProductsChart');
    const countryCanvas = document.getElementById('countryChart');

    const basketTableBody = document.querySelector('#basket-table tbody');
    const runBasketBtn = document.getElementById('run-basket-btn');

    let API_URL = '';
    let salesChartInst = null;
    let topProductsChartInst = null;
    let countryChartInst = null;

    function log(msg) {
        if (!debugLog) return;
        const time = new Date().toLocaleTimeString();
        debugLog.innerHTML += `<br>[${time}] <span style="color:#fff">${msg}</span>`;
        console.log(msg);
        debugLog.scrollTop = debugLog.scrollHeight;

        // Auto-detect backend crash
        if (msg.includes("Connection refused") || msg.includes("Errno 111")) {
            statusInd.innerHTML = '<span class="dot" style="background:var(--error)"></span> Backend Crashed';
            alert("CRITICAL ERROR: The Colab Backend has crashed.\n\nYou must:\n1. Go to Colab -> Runtime -> Restart Session\n2. Run All Cells\n3. Connect with the NEW URL.");
        }
    }

    const headers = { 'ngrok-skip-browser-warning': 'true' };

    // --- Connectivity ---
    connectBtn.addEventListener('click', async () => {
        let url = ngrokInput.value.trim();
        if (url.endsWith('/')) url = url.slice(0, -1);
        if (!url) { alert("Please enter a valid URL"); return; }

        API_URL = url;
        localStorage.setItem('ngrok_url', url);
        uploadSection.classList.remove('hidden');
        uploadSection.style.display = 'block';

        log(`Setting URL to: ${url}`);
        statusInd.innerHTML = '<span class="dot"></span> Verifying...';

        try {
            const res = await fetch(`${url}/`, { headers });
            if (res.ok) {
                statusInd.innerHTML = '<span class="dot connected"></span> Connected';
                log("Backend Connected.");
            } else {
                throw new Error(`Status ${res.status}`);
            }
        } catch (e) {
            log(`Connectivity Check Warning: ${e.message}`);
            statusInd.innerHTML = '<span class="dot" style="background:orange"></span> Weak Connection';
        }
    });

    const savedUrl = localStorage.getItem('ngrok_url');
    if (savedUrl) ngrokInput.value = savedUrl;

    // --- Upload ---
    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.style.borderColor = 'var(--primary)'; });
    dropZone.addEventListener('dragleave', (e) => { e.preventDefault(); dropZone.style.borderColor = 'var(--glass-border)'; });
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = 'var(--glass-border)';
        if (e.dataTransfer.files.length) handleFileUpload(e.dataTransfer.files[0]);
    });
    fileInput.addEventListener('change', (e) => { if (e.target.files.length) handleFileUpload(e.target.files[0]); });

    async function handleFileUpload(file) {
        log(`Uploading file: ${file.name}...`);
        const formData = new FormData();
        formData.append('file', file);

        try {
            const res = await fetch(`${API_URL}/upload`, { method: 'POST', headers, body: formData });
            if (res.ok) {
                log("Upload success! Starting full analysis...");
                fileInfo.innerHTML = `<span style="color:var(--success)">✓ Uploaded: ${file.name}</span>`;

                resultsSection.classList.remove('hidden');
                kpiSection.classList.remove('hidden');

                // Trigger all analyses
                fetchKPIs();
                fetchSalesAnalysis();
                fetchTopProducts();
                fetchCountryAnalysis();
                fetchBasketAnalysis();
            } else {
                const data = await res.json();
                throw new Error(data.error || 'Upload failed');
            }
        } catch (e) {
            log(`Upload Error: ${e.message}`);
            fileInfo.innerHTML = `<span style="color:var(--error)">✗ Error: ${e.message}</span>`;
        }
    }

    // --- New Analysis Functions ---
    async function fetchKPIs() {
        try {
            log("Fetching KPIs...");
            const res = await fetch(`${API_URL}/analyze/summary`, { headers });

            // Check for HTML error
            const contentType = res.headers.get("content-type");
            if (contentType && contentType.includes("text/html")) {
                log("KPI Error: Received HTML Response");
                throw new Error("Server Error (HTML Response)");
            }

            const data = await res.json();
            if (res.ok) {
                log(`KPI Data Received: ${JSON.stringify(data)}`);
                document.getElementById('kpi-revenue').textContent = `£${(data.total_revenue || 0).toLocaleString(undefined, { maximumFractionDigits: 0 })}`;
                document.getElementById('kpi-orders').textContent = (data.total_transactions || 0).toLocaleString();
                document.getElementById('kpi-customers').textContent = (data.total_customers || 0).toLocaleString();
                document.getElementById('kpi-items').textContent = (data.total_items || 0).toLocaleString();
            } else {
                throw new Error(data.error || "Unknown Error");
            }
        } catch (e) {
            log("KPI Error: " + e.message);
            ['kpi-revenue', 'kpi-orders', 'kpi-customers', 'kpi-items'].forEach(id => {
                document.getElementById(id).textContent = "N/A";
                document.getElementById(id).style.color = "var(--error)";
            });
        }
    }

    async function fetchTopProducts() {
        try {
            const res = await fetch(`${API_URL}/analyze/top_products`, { headers });
            const data = await res.json();
            if (res.ok) renderTopProductsChart(data);
        } catch (e) { log("Top Products Error: " + e.message); }
    }

    async function fetchCountryAnalysis() {
        try {
            const res = await fetch(`${API_URL}/analyze/by_country`, { headers });
            const data = await res.json();
            if (res.ok) renderCountryChart(data);
        } catch (e) { log("Country Error: " + e.message); }
    }

    // --- Original Analysis Functions ---
    async function fetchSalesAnalysis() {
        try {
            const res = await fetch(`${API_URL}/analyze/sales`, { headers });
            const data = await res.json();
            if (res.ok && data.length) {
                log(`Sales Data Received: ${data.length} records`);
                renderSalesChart(data);
            } else if (!data.length) {
                log(`Sales Warning: Empty Data. Raw Response: ${JSON.stringify(data)}`);
            }
        } catch (e) { log(`Sales Error: ${e.message}`); }
    }

    runBasketBtn.addEventListener('click', fetchBasketAnalysis);

    async function fetchBasketAnalysis() {
        const minSup = document.getElementById('min-sup').value;
        const minConf = document.getElementById('min-conf').value;
        basketTableBody.innerHTML = '<tr><td colspan="4" style="text-align:center">Analyzing...</td></tr>';

        try {
            const res = await fetch(`${API_URL}/analyze/basket?min_support=${minSup}&min_confidence=${minConf}`, { headers });

            const contentType = res.headers.get("content-type");
            if (contentType && contentType.includes("text/html")) {
                const text = await res.text();
                const titleMatch = text.match(/<title>(.*?)<\/title>/i);
                const h1Match = text.match(/<h1>(.*?)<\/h1>/i);
                const errorInfo = titleMatch ? titleMatch[1] : (h1Match ? h1Match[1] : "Received HTML Response (likely error page)");
                throw new Error(`Server Error: ${errorInfo}`);
            }

            const data = await res.json();
            if (res.ok) renderBasketTable(data);
            else throw new Error(data.error);
        } catch (e) {
            log(`Basket Error: ${e.message}`);
            basketTableBody.innerHTML = `<tr><td colspan="4" style="color:var(--error)">Error: ${e.message}</td></tr>`;
        }
    }

    // --- Rendering ---
    const commonChartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { labels: { color: 'white' } } },
        scales: {
            y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#a0a0a0' } },
            x: { grid: { display: false }, ticks: { color: '#a0a0a0' } }
        }
    };

    function renderSalesChart(data) {
        if (salesChartInst) salesChartInst.destroy();
        salesChartInst = new Chart(salesChartCanvas.getContext('2d'), {
            type: 'line',
            data: {
                labels: data.map(d => d.Date),
                datasets: [{
                    label: 'Daily Sales (£)',
                    data: data.map(d => d.DailySales),
                    borderColor: '#4dabf7',
                    backgroundColor: 'rgba(77, 171, 247, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: commonChartOptions
        });
    }

    function renderTopProductsChart(data) {
        if (topProductsChartInst) topProductsChartInst.destroy();
        topProductsChartInst = new Chart(topProductsCanvas.getContext('2d'), {
            type: 'bar',
            data: {
                labels: data.map(d => d.Description ? d.Description.substring(0, 15) + '...' : d.StockCode),
                datasets: [{
                    label: 'Revenue (£)',
                    data: data.map(d => d.Revenue),
                    backgroundColor: ['#f06595', '#da77f2', '#be4bdb', '#845ef7', '#5c7cfa'],
                    borderRadius: 4
                }]
            },
            options: commonChartOptions
        });
    }

    function renderCountryChart(data) {
        if (countryChartInst) countryChartInst.destroy();
        countryChartInst = new Chart(countryCanvas.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: data.map(d => d.Country),
                datasets: [{
                    data: data.map(d => d.Revenue),
                    backgroundColor: [
                        '#4dabf7', '#3bc9db', '#38d9a9', '#69db7c', '#a9e34b',
                        '#fcc419', '#ff922b', '#ff6b6b', '#f06595', '#cc5de8'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'right', labels: { color: 'white', font: { size: 10 } } }
                }
            }
        });
    }

    function renderBasketTable(rules) {
        basketTableBody.innerHTML = '';
        if (!rules.length) { basketTableBody.innerHTML = '<tr><td colspan="4" style="text-align:center">No rules found.</td></tr>'; return; }

        rules.forEach(rule => {
            const tr = document.createElement('tr');
            const ant = Array.isArray(rule.antecedent) ? rule.antecedent : [rule.antecedent];
            const con = Array.isArray(rule.consequent) ? rule.consequent : [rule.consequent];

            tr.innerHTML = `
                <td>${ant.map(i => `<span class="box">${i}</span>`).join('')}</td>
                <td>${con.map(i => `<span class="box" style="background:rgba(0,210,106,0.1)">${i}</span>`).join('')}</td>
                <td>${(rule.confidence * 100).toFixed(1)}%</td>
                <td>${rule.lift.toFixed(2)}</td>
            `;
            basketTableBody.appendChild(tr);
        });
    }
});
