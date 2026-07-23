// Official Cortes and FLP Table Definition (Image 1)
const CORTES_DATA = [
    { corte: 3,  asig_dia: 4,  flp_dia: 26, retiro_dia: 3,  dias_c1: 27, dias_c2: 3 },
    { corte: 5,  asig_dia: 6,  flp_dia: 28, retiro_dia: 5,  dias_c1: 25, dias_c2: 5 },
    { corte: 8,  asig_dia: 9,  flp_dia: 1,  retiro_dia: 8,  dias_c1: 22, dias_c2: 8 },
    { corte: 10, asig_dia: 11, flp_dia: 3,  retiro_dia: 10, dias_c1: 20, dias_c2: 10 },
    { corte: 11, asig_dia: 12, flp_dia: 4,  retiro_dia: 11, dias_c1: 19, dias_c2: 11 },
    { corte: 15, asig_dia: 16, flp_dia: 8,  retiro_dia: 15, dias_c1: 15, dias_c2: 15 },
    { corte: 19, asig_dia: 20, flp_dia: 12, retiro_dia: 19, dias_c1: 11, dias_c2: 19 },
    { corte: 20, asig_dia: 21, flp_dia: 13, retiro_dia: 20, dias_c1: 10, dias_c2: 20 },
    { corte: 23, asig_dia: 24, flp_dia: 16, retiro_dia: 23, dias_c1: 7,  dias_c2: 23 },
    { corte: 25, asig_dia: 26, flp_dia: 18, retiro_dia: 25, dias_c1: 5,  dias_c2: 25 },
    { corte: 28, asig_dia: 29, flp_dia: 21, retiro_dia: 28, dias_c1: 2,  dias_c2: 28 }
];

// Official Fee Schedule Matrix (Image 2)
const FEE_RATES = {
    "1 PV": {
        "120+":    { contencion: 0.0412, parcial: 0.0288, indirecto: 0.0103 },
        "110-120": { contencion: 0.0375, parcial: 0.0263, indirecto: 0.0094 },
        "100-110": { contencion: 0.0350, parcial: 0.0245, indirecto: 0.0088 },
        "0-100":   { contencion: 0.0325, parcial: 0.0228, indirecto: 0.0081 }
    },
    "2 PV": {
        "120+":    { contencion: 0.0660, parcial: 0.0462, indirecto: 0.0165 },
        "110-120": { contencion: 0.0601, parcial: 0.0421, indirecto: 0.0150 },
        "100-110": { contencion: 0.0560, parcial: 0.0392, indirecto: 0.0140 },
        "0-100":   { contencion: 0.0519, parcial: 0.0363, indirecto: 0.0130 }
    }
};

// Helper: Determine if payment falls into Ciclo 1 or Ciclo 2 for month 07
// Day >= asig_dia in July => Ciclo 1 (New assignment for July)
// Day < asig_dia in July => Ciclo 2 (Tail end of previous June assignment)
function checkIsCiclo1(corteObj, dayOfMonth) {
    return dayOfMonth >= corteObj.asig_dia;
}

// Global Chart References
let segmentStackedChartInstance = null;
let cicloDonutChartInstance = null;
let corteBarChartInstance = null;

// Demo Payments Dataset (Month 07 - July)
let paymentsData = [];

// Helper: Format Currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('es-MX', {
        style: 'currency',
        currency: 'MXN',
        minimumFractionDigits: 2
    }).format(amount);
}

// Helper: Format Percentage
function formatPct(value) {
    return value.toFixed(2) + '%';
}

// Real Database Metrics (Live Connection & Updated Baseline from Aiven MySQL)
let REAL_DB_SEGMENT_STATS = {
    "1 PV": {
        "total": 18175475.99,
        "c1": 3894822.05,
        "c2": 14280653.94
    },
    "2 PV": {
        "total": 3687686.61,
        "c1": 571760.19,
        "c2": 3115926.42
    }
};

let REAL_DB_CORTE_STATS = {
    3:  { c1: 10130.68,   c2: 500.00,       total: 10630.68 },
    5:  { c1: 12966.00,   c2: 0.00,         total: 12966.00 },
    8:  { c1: 567645.22,  c2: 359436.00,    total: 927081.22 },
    10: { c1: 2666495.91, c2: 2112000.00,   total: 4778495.91 },
    11: { c1: 88658.00,   c2: 169420.00,    total: 258078.00 },
    15: { c1: 1100200.00, c2: 2207100.00,   total: 3307300.00 },
    19: { c1: 3311.90,    c2: 190680.00,    total: 193991.90 },
    20: { c1: 0.00,       c2: 2401340.00,   total: 2401340.00 },
    23: { c1: 0.00,       c2: 3111000.00,   total: 3111000.00 },
    25: { c1: 0.00,       c2: 5006838.89,   total: 5006838.89 },
    28: { c1: 0.00,       c2: 1755440.00,   total: 1755440.00 }
};

// Fetch real-time aggregated metrics from Aiven DB API
async function fetchLiveMetricsFromAiven() {
    const badge = document.getElementById('liveStatusBadge');
    const btn = document.getElementById('btnLoadDemo');

    if (btn) {
        btn.querySelector('i').classList.add('fa-spin');
    }

    try {
        const response = await fetch('/api/metrics', { cache: 'no-store' });
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const data = await response.json();

        if (data.status === 'success' && data.segmentStats && data.corteStats) {
            REAL_DB_SEGMENT_STATS = data.segmentStats;
            REAL_DB_CORTE_STATS = data.corteStats;

            const timeStr = new Date().toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit', second: '2-digit' });

            if (badge) {
                badge.style.display = 'inline-flex';
                badge.className = 'live-status-badge';
                badge.innerHTML = `<i class="fa-solid fa-circle-dot text-success animate-pulse"></i> <span>Aiven DB: En Vivo</span> <small>(${timeStr})</small>`;
            }

            renderDashboard();
        } else {
            throw new Error('Respuesta inválida del servidor');
        }
    } catch (err) {
        console.log('Utilizando datos estandar:', err.message);
        if (badge) {
            badge.style.display = 'none';
        }
    } finally {
        if (btn) {
            btn.querySelector('i').classList.remove('fa-spin');
        }
    }
}


function generateDemoData() {
    paymentsData = [];
}

// Calculate Metrics using Real Database Figures
function calculateMetrics() {
    const selectedProdTier = document.getElementById('prodTierSelect').value;
    const contencionPct = parseFloat(document.getElementById('contencionPctSelect').value) / 100;
    const parcialPct = 1 - contencionPct;

    // 1. Segment Breakdown (Only 1 PV and 2 PV)
    const segmentStats = JSON.parse(JSON.stringify(REAL_DB_SEGMENT_STATS));

    // 2. Corte Breakdown Aggregation
    const corteStats = {};
    let globalContencionC1 = 0;
    let globalContencionC2 = 0;

    CORTES_DATA.forEach(c => {
        const realC = REAL_DB_CORTE_STATS[c.corte] || { c1: 0, c2: 0, total: 0 };
        const cont1 = realC.c1 * contencionPct;
        const cont2 = realC.c2 * contencionPct;
        globalContencionC1 += cont1;
        globalContencionC2 += cont2;
        corteStats[c.corte] = {
            ...c,
            c1: realC.c1,
            c2: realC.c2,
            contencion1: cont1,
            contencion2: cont2,
            total: realC.total
        };
    });

    let globalTotal = segmentStats["1 PV"].total + segmentStats["2 PV"].total;
    let globalC1 = segmentStats["1 PV"].c1 + segmentStats["2 PV"].c1;
    let globalC2 = segmentStats["1 PV"].c2 + segmentStats["2 PV"].c2;

    // 3. Billing Calculations
    let globalFacturacion = 0;

    Object.keys(segmentStats).forEach(seg => {
        const rates = FEE_RATES[seg][selectedProdTier] || FEE_RATES["1 PV"][selectedProdTier];
        // Weighted fee percentage based on contención ratio
        const effectiveRate = (rates.contencion * contencionPct) + (rates.parcial * parcialPct);
        
        segmentStats[seg].effectiveRate = effectiveRate;
        segmentStats[seg].factC1 = segmentStats[seg].c1 * effectiveRate;
        segmentStats[seg].factC2 = segmentStats[seg].c2 * effectiveRate;
        segmentStats[seg].factTotal = segmentStats[seg].total * effectiveRate;

        globalFacturacion += segmentStats[seg].factTotal;
    });

    return {
        globalTotal,
        globalC1,
        globalC2,
        globalContencionC1,
        globalContencionC2,
        globalFacturacion,
        segmentStats,
        corteStats
    };
}

// Render Dashboard UI
function renderDashboard() {
    const metrics = calculateMetrics();

    // 1. Render KPIs
    document.getElementById('kpiTotalAmount').innerText = formatCurrency(metrics.globalTotal);
    document.getElementById('kpiCiclo1Amount').innerText = formatCurrency(metrics.globalC1);
    document.getElementById('kpiCiclo2Amount').innerText = formatCurrency(metrics.globalC2);

    const c1Pct = metrics.globalTotal > 0 ? (metrics.globalC1 / metrics.globalTotal) * 100 : 0;
    const c2Pct = metrics.globalTotal > 0 ? (metrics.globalC2 / metrics.globalTotal) * 100 : 0;

    document.getElementById('kpiCiclo1Pct').innerText = `${formatPct(c1Pct)} del total`;
    document.getElementById('kpiCiclo2Pct').innerText = `${formatPct(c2Pct)} del total`;

    document.getElementById('kpiFacturacionTotal').innerText = formatCurrency(metrics.globalFacturacion);
    const effRate = metrics.globalTotal > 0 ? (metrics.globalFacturacion / metrics.globalTotal) * 100 : 0;
    document.getElementById('kpiTasaEfectiva').innerText = `Tasa promedio efectiva: ${formatPct(effRate)}`;

    // 2. Render Segment Table
    const segTbody = document.querySelector('#tableSegmentBreakdown tbody');
    segTbody.innerHTML = '';

    let totC1Fact = 0, totC2Fact = 0;

    Object.keys(metrics.segmentStats).forEach(seg => {
        const s = metrics.segmentStats[seg];
        const segC1Pct = s.total > 0 ? (s.c1 / s.total) * 100 : 0;
        const segC2Pct = s.total > 0 ? (s.c2 / s.total) * 100 : 0;

        totC1Fact += s.factC1;
        totC2Fact += s.factC2;

        const tagClass = seg === '1 PV' ? 'tag-1pv' : (seg === '2 PV' ? 'tag-2pv' : 'tag-prev');

        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><span class="tag ${tagClass}">${seg}</span></td>
            <td><strong>${formatCurrency(s.total)}</strong></td>
            <td>${formatCurrency(s.c1)}</td>
            <td><span class="badge-c1 kpi-badge">${formatPct(segC1Pct)}</span></td>
            <td>${formatCurrency(s.factC1)}</td>
            <td>${formatCurrency(s.c2)}</td>
            <td><span class="badge-c2 kpi-badge">${formatPct(segC2Pct)}</span></td>
            <td>${formatCurrency(s.factC2)}</td>
            <td><strong style="color: #60a5fa;">${formatCurrency(s.factTotal)}</strong></td>
            <td><strong>${formatPct(s.effectiveRate * 100)}</strong></td>
        `;
        segTbody.appendChild(tr);
    });

    // Segment Table Totals
    document.getElementById('totRecuperado').innerText = formatCurrency(metrics.globalTotal);
    document.getElementById('totC1Recuperado').innerText = formatCurrency(metrics.globalC1);
    document.getElementById('totC1Pct').innerText = formatPct(c1Pct);
    document.getElementById('totC1Fact').innerText = formatCurrency(totC1Fact);
    document.getElementById('totC2Recuperado').innerText = formatCurrency(metrics.globalC2);
    document.getElementById('totC2Pct').innerText = formatPct(c2Pct);
    document.getElementById('totC2Fact').innerText = formatCurrency(totC2Fact);
    document.getElementById('totFacturable').innerText = formatCurrency(metrics.globalFacturacion);
    document.getElementById('totFeeProm').innerText = formatPct(effRate);

    // 3. Render Cortes Table
    const cortesTbody = document.querySelector('#tableCortes tbody');
    cortesTbody.innerHTML = '';

    let sumCorteC1 = 0, sumCorteC2 = 0, sumCorteCont1 = 0, sumCorteCont2 = 0, sumCorteTotal = 0;

    CORTES_DATA.forEach(c => {
        const cs = metrics.corteStats[c.corte];
        const corteC1Pct = cs.total > 0 ? (cs.c1 / cs.total) * 100 : 0;
        const corteC2Pct = cs.total > 0 ? (cs.c2 / cs.total) * 100 : 0;

        sumCorteC1 += cs.c1;
        sumCorteC2 += cs.c2;
        sumCorteCont1 += cs.contencion1;
        sumCorteCont2 += cs.contencion2;
        sumCorteTotal += cs.total;

        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><strong>Corte ${c.corte}</strong></td>
            <td>Día ${c.flp_dia}</td>
            <td>Día ${c.asig_dia}</td>
            <td>${c.dias_c1} días</td>
            <td>${c.dias_c2} días</td>
            <td>${formatCurrency(cs.c1)}</td>
            <td>${formatCurrency(cs.c2)}</td>
            <td><strong style="color: #10b981;">${formatCurrency(cs.contencion1)}</strong></td>
            <td><strong style="color: #f59e0b;">${formatCurrency(cs.contencion2)}</strong></td>
            <td><strong>${formatCurrency(cs.total)}</strong></td>
            <td>
                <span class="badge-c1 kpi-badge">${formatPct(corteC1Pct)}</span> / 
                <span class="badge-c2 kpi-badge">${formatPct(corteC2Pct)}</span>
            </td>
        `;
        cortesTbody.appendChild(tr);
    });

    if (document.getElementById('totCorteC1')) {
        document.getElementById('totCorteC1').innerText = formatCurrency(sumCorteC1);
        document.getElementById('totCorteC2').innerText = formatCurrency(sumCorteC2);
        document.getElementById('totCorteCont1').innerText = formatCurrency(sumCorteCont1);
        document.getElementById('totCorteCont2').innerText = formatCurrency(sumCorteCont2);
        document.getElementById('totCorteTotal').innerText = formatCurrency(sumCorteTotal);
    }

    // 4. Render Charts
    renderCharts(metrics);
}

// Render Charts Function
function renderCharts(metrics) {
    // A. Stacked Bar Chart (Segment vs Cycle)
    const ctxSegment = document.getElementById('segmentStackedChart').getContext('2d');
    const segLabels = Object.keys(metrics.segmentStats);
    const c1Data = segLabels.map(s => metrics.segmentStats[s].c1);
    const c2Data = segLabels.map(s => metrics.segmentStats[s].c2);

    if (segmentStackedChartInstance) segmentStackedChartInstance.destroy();

    segmentStackedChartInstance = new Chart(ctxSegment, {
        type: 'bar',
        data: {
            labels: segLabels,
            datasets: [
                {
                    label: 'Ciclo 1 (≤ FLP)',
                    data: c1Data,
                    backgroundColor: '#10b981',
                    borderRadius: 6
                },
                {
                    label: 'Ciclo 2 (> FLP)',
                    data: c2Data,
                    backgroundColor: '#f59e0b',
                    borderRadius: 6
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { labels: { color: '#94a3b8' } },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${formatCurrency(context.raw)}`;
                        }
                    }
                }
            },
            scales: {
                x: { stacked: true, ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' } },
                y: { 
                    stacked: true, 
                    ticks: { 
                        color: '#94a3b8',
                        callback: function(val) { return '$' + (val / 1000).toFixed(0) + 'k'; }
                    },
                    grid: { color: 'rgba(255,255,255,0.05)' } 
                }
            }
        }
    });

    // B. Donut Chart (Total Ciclo 1 vs Ciclo 2)
    const ctxDonut = document.getElementById('cicloDonutChart').getContext('2d');
    
    if (cicloDonutChartInstance) cicloDonutChartInstance.destroy();

    cicloDonutChartInstance = new Chart(ctxDonut, {
        type: 'doughnut',
        data: {
            labels: ['Ciclo 1 (≤ FLP)', 'Ciclo 2 (> FLP)'],
            datasets: [{
                data: [metrics.globalC1, metrics.globalC2],
                backgroundColor: ['#10b981', '#f59e0b'],
                borderWidth: 2,
                borderColor: '#1e293b'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom', labels: { color: '#94a3b8' } },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const total = metrics.globalTotal;
                            const pct = total > 0 ? (context.raw / total) * 100 : 0;
                            return `${context.label}: ${formatCurrency(context.raw)} (${formatPct(pct)})`;
                        }
                    }
                }
            }
        }
    });

    // C. Bar Chart by Corte
    const ctxCorte = document.getElementById('corteBarChart').getContext('2d');
    const corteLabels = CORTES_DATA.map(c => `Corte ${c.corte}`);
    const corteC1Data = CORTES_DATA.map(c => metrics.corteStats[c.corte].c1);
    const corteC2Data = CORTES_DATA.map(c => metrics.corteStats[c.corte].c2);

    if (corteBarChartInstance) corteBarChartInstance.destroy();

    corteBarChartInstance = new Chart(ctxCorte, {
        type: 'bar',
        data: {
            labels: corteLabels,
            datasets: [
                { label: 'Ciclo 1', data: corteC1Data, backgroundColor: '#10b981', borderRadius: 4 },
                { label: 'Ciclo 2', data: corteC2Data, backgroundColor: '#f59e0b', borderRadius: 4 }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { labels: { color: '#94a3b8' } },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${formatCurrency(context.raw)}`;
                        }
                    }
                }
            },
            scales: {
                x: { ticks: { color: '#94a3b8', font: { size: 10 } }, grid: { color: 'rgba(255,255,255,0.05)' } },
                y: { 
                    ticks: { 
                        color: '#94a3b8',
                        callback: function(val) { return '$' + (val / 1000).toFixed(0) + 'k'; }
                    }, 
                    grid: { color: 'rgba(255,255,255,0.05)' } 
                }
            }
        }
    });
}

// Parse TSV/CSV or pasted SQL query output
function parseAndLoadPastedData(rawText) {
    if (!rawText || !rawText.trim()) return false;

    const lines = rawText.trim().split(/\r?\n/);
    const parsedPayments = [];

    lines.forEach((line, index) => {
        const cols = line.split(/[\t,;|]/).map(c => c.trim().replace(/^["']|["']$/g, ''));
        if (cols.length < 3) return;

        let segRaw = cols[0];
        let montoVal = parseFloat(cols[1]);
        let corteVal = parseInt(cols[3] || cols[2]);

        if (isNaN(montoVal)) return;

        let tipoAsig = (segRaw === '1' || segRaw === '1 PV') ? '1' : '2';
        let segName = tipoAsig === '1' ? '1 PV' : '2 PV';

        if (segRaw === 'PREV') return;

        let corteObj = CORTES_DATA.find(c => c.corte === corteVal) || CORTES_DATA[0];

        let dayOfPayment = corteObj.asig_dia;
        for (let c of cols) {
            if (/^\d{4}-\d{2}-\d{2}$/.test(c)) {
                dayOfPayment = parseInt(c.split('-')[2]);
            }
        }

        parsedPayments.push({
            id: index + 1,
            corte: corteObj.corte,
            asig_dia: corteObj.asig_dia,
            flp_dia: corteObj.flp_dia,
            retiro_dia: corteObj.retiro_dia,
            fecha_pago: `2026-07-${String(dayOfPayment).padStart(2, '0')}`,
            day_of_payment: dayOfPayment,
            monto: montoVal,
            espagogestion: 1,
            tipo_asignacion: tipoAsig,
            pago_descuento: 1,
            segmento: segName,
            isCiclo1: checkIsCiclo1(corteObj, dayOfPayment)
        });
    });

    if (parsedPayments.length > 0) {
        paymentsData = parsedPayments;
        renderDashboard();
        return true;
    }
    return false;
}

// Event Listeners Setup
function setupEventListeners() {
    document.getElementById('prodTierSelect').addEventListener('change', () => {
        updateHighlightTier();
        renderDashboard();
    });

    document.getElementById('contencionPctSelect').addEventListener('change', renderDashboard);

    document.getElementById('btnLoadDemo').addEventListener('click', () => {
        fetchLiveMetricsFromAiven();
    });

    document.getElementById('btnCopySql').addEventListener('click', () => {
        const sqlText = document.getElementById('sqlCodeText').innerText;
        navigator.clipboard.writeText(sqlText).then(() => {
            const btn = document.getElementById('btnCopySql');
            btn.innerHTML = '<i class="fa-solid fa-check"></i> ¡Copiado!';
            btn.classList.add('btn-secondary');
            setTimeout(() => {
                btn.innerHTML = '<i class="fa-solid fa-copy"></i> Copiar SQL';
                btn.classList.remove('btn-secondary');
            }, 2000);
        });
    });

    // Modal Events
    const importModal = document.getElementById('importModal');
    const btnOpenModal = document.getElementById('btnOpenModal');
    const btnCloseModal = document.getElementById('btnCloseModal');
    const btnCancelModal = document.getElementById('btnCancelModal');
    const btnProcessPaste = document.getElementById('btnProcessPaste');
    const txtSqlPaste = document.getElementById('txtSqlPaste');

    btnOpenModal.addEventListener('click', () => importModal.classList.remove('hidden'));
    btnCloseModal.addEventListener('click', () => importModal.classList.add('hidden'));
    btnCancelModal.addEventListener('click', () => importModal.classList.add('hidden'));

    btnProcessPaste.addEventListener('click', () => {
        const success = parseAndLoadPastedData(txtSqlPaste.value);
        if (success) {
            importModal.classList.add('hidden');
            txtSqlPaste.value = '';
        } else {
            alert('No se pudieron procesar las filas. Asegúrate de incluir columnas: segmento, monto, espagogestion, corte (o fecha_pago).');
        }
    });
}

// Highlight Active Tier in Fee Tables
function updateHighlightTier() {
    const tierMap = {
        '120+': 'tier-120',
        '110-120': 'tier-110-120',
        '100-110': 'tier-100-110',
        '0-100': 'tier-0-100'
    };
    const activeTier = document.getElementById('prodTierSelect').value;
    const targetClass = tierMap[activeTier];

    document.querySelectorAll('.fee-mini-table tr').forEach(tr => tr.classList.remove('highlight-tier'));
    document.querySelectorAll(`.fee-mini-table .${targetClass}`).forEach(tr => tr.classList.add('highlight-tier'));
}

// Initialize Application with Live Aiven Sync & Auto-Refresh
document.addEventListener('DOMContentLoaded', () => {
    generateDemoData();
    setupEventListeners();
    updateHighlightTier();
    renderDashboard();
    
    // Initial fetch from live Aiven DB API
    fetchLiveMetricsFromAiven();

    // Auto-refresh every 30 seconds
    setInterval(fetchLiveMetricsFromAiven, 30000);
});

