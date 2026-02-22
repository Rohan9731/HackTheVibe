/**
 * VibeShield v2.0 — Dashboard Charts & Stats
 */

let dailyChartInst = null;
let categoryChartInst = null;

document.addEventListener('DOMContentLoaded', () => { loadDashboard(); loadDashboardContext(); });

async function loadDashboardContext() {
    try {
        const [ctxRes, setRes] = await Promise.all([
            fetch('/api/transactions/context'),
            fetch('/api/transactions/settings')
        ]);
        const ctx = await ctxRes.json();
        const settings = await setRes.json();
        if (ctx.mood_status) {
            const m = ctx.mood_status;
            document.getElementById('cmMood').textContent = `${m.emoji || ''} ${m.mood || 'Unknown'}`.trim();
        }
        if (ctx.active_goal) {
            const g = ctx.active_goal;
            document.getElementById('cmGoal').textContent = `${g.name}: ${g.progress.toFixed(0)}%`;
        }
        if (ctx.top_trigger) {
            const t = ctx.top_trigger;
            document.getElementById('cmTrigger').textContent = `${t.category} (${t.count}x)`;
        }
        if (settings.lock_sensitivity) document.getElementById('cmSensitivity').textContent = settings.lock_sensitivity.charAt(0).toUpperCase() + settings.lock_sensitivity.slice(1);
    } catch(e) { console.error('Dashboard context error', e); }
}

async function loadDashboard() {
    try {
        const res = await fetch('/api/dashboard/stats');
        const data = await res.json();
        if (data.error) return;
        renderStats(data);
        renderLevel(data.level, data.cancelled_count);
        renderDailyChart(data.daily_spending);
        renderCategoryChart(data.category_breakdown);
        renderGoals(data.savings_goals);
        renderContacts(data.contacts);
        renderDashRecent(data.recent_transactions);
    } catch (e) { console.error(e); }
}

function renderStats(d) {
    animateValue('statTx', d.total_transactions);
    animateTextValue('statSpent', d.total_spent, '₹');
    animateTextValue('statSaved', d.money_saved, '₹');
    animateValue('statStreak', d.self_control_streak);
    animateValue('statAvgScore', d.avg_impulse_score);
}

function animateValue(id, target) {
    const el = document.getElementById(id);
    const duration = 800;
    const start = performance.now();
    function update(now) {
        const p = Math.min((now - start) / duration, 1);
        const eased = 1 - Math.pow(1 - p, 3);
        el.textContent = Math.round(target * eased);
        if (p < 1) requestAnimationFrame(update);
    }
    requestAnimationFrame(update);
}

function animateTextValue(id, target, prefix = '') {
    const el = document.getElementById(id);
    const duration = 800;
    const start = performance.now();
    function update(now) {
        const p = Math.min((now - start) / duration, 1);
        const eased = 1 - Math.pow(1 - p, 3);
        el.textContent = prefix + Math.round(target * eased).toLocaleString();
        if (p < 1) requestAnimationFrame(update);
    }
    requestAnimationFrame(update);
}

function renderLevel(level, saves) {
    document.getElementById('levelEmoji').textContent = level.emoji;
    document.getElementById('levelName').textContent = level.name;
    document.getElementById('levelTier').textContent = 'Tier ' + level.tier;
    const thresholds = [1, 2, 5, 10, 20];
    const next = thresholds.find(t => t > saves) || 20;
    const prev = thresholds[thresholds.indexOf(next) - 1] || 0;
    const pct = Math.min(100, ((saves - prev) / (next - prev)) * 100);
    document.getElementById('levelFill').style.width = pct + '%';
    document.getElementById('levelHint').textContent =
        saves >= 20 ? 'Max level reached! 🧘' :
        `${next - saves} more saves to next level`;
}

function renderDailyChart(daily) {
    const labels = Object.keys(daily).sort();
    if (labels.length === 0) {
        document.getElementById('dailyEmpty').classList.remove('hidden');
        return;
    }
    document.getElementById('dailyEmpty').classList.add('hidden');
    const vals = labels.map(l => daily[l]);
    if (dailyChartInst) dailyChartInst.destroy();
    dailyChartInst = new Chart(document.getElementById('dailyChart'), {
        type: 'line',
        data: {
            labels: labels.map(l => l.slice(5)),  // MM-DD
            datasets: [{
                label: 'Daily Spending (₹)',
                data: vals,
                borderColor: '#6c5ce7',
                backgroundColor: 'rgba(108,92,231,0.1)',
                fill: true, tension: 0.4, pointRadius: 3,
                pointBackgroundColor: '#6c5ce7',
            }]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { ticks: { color: '#8892b0', maxTicksLimit: 10 }, grid: { color: 'rgba(255,255,255,0.05)' } },
                y: { ticks: { color: '#8892b0', callback: v => '₹' + v.toLocaleString() }, grid: { color: 'rgba(255,255,255,0.05)' } }
            }
        }
    });
}

function renderCategoryChart(cats) {
    const labels = Object.keys(cats);
    if (labels.length === 0) {
        document.getElementById('categoryEmpty').classList.remove('hidden');
        return;
    }
    document.getElementById('categoryEmpty').classList.add('hidden');
    const vals = labels.map(l => cats[l]);
    const colors = ['#ff4757','#ffa502','#2ed573','#6c5ce7','#1e90ff','#a55eea','#ff6b81','#70a1ff','#eccc68','#ff9ff3','#48dbfb','#f368e0'];
    if (categoryChartInst) categoryChartInst.destroy();
    categoryChartInst = new Chart(document.getElementById('categoryChart'), {
        type: 'doughnut',
        data: {
            labels: labels.map(l => l.replace('_',' ').replace(/\b\w/g,c=>c.toUpperCase())),
            datasets: [{ data: vals, backgroundColor: colors.slice(0, labels.length), borderWidth: 0 }]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            plugins: { legend: { position: 'right', labels: { color: '#ccd6f6', font: { size: 11 }, padding: 8 } } },
            cutout: '65%',
        }
    });
}

function renderGoals(goals) {
    const el = document.getElementById('goalsList');
    if (!goals || goals.length === 0) {
        el.innerHTML = '<p class="empty-text">No savings goals yet. Add one below!</p>';
        return;
    }
    el.innerHTML = goals.map(g => {
        const pct = Math.min(100, (g.current_amount / g.target_amount * 100)).toFixed(0);
        return `<div class="goal-item">
            <span class="goal-name">🎯 ${g.name}</span>
            <div class="goal-progress">
                <div class="goal-bar"><div class="goal-bar-fill" style="width:${pct}%"></div></div>
                <span>₹${g.current_amount.toLocaleString()} / ₹${g.target_amount.toLocaleString()} (${pct}%)</span>
            </div>
        </div>`;
    }).join('');
}

function renderContacts(contacts) {
    const el = document.getElementById('contactsList');
    if (!contacts || contacts.length === 0) {
        el.innerHTML = '<p class="empty-text">No accountability contacts. Add one below!</p>';
        return;
    }
    el.innerHTML = contacts.map(c =>
        `<div class="contact-item"><span>👤 ${c.name}</span><span style="color:var(--text-muted)">${c.phone || c.email || ''}</span></div>`
    ).join('');
}

function renderDashRecent(txs) {
    const el = document.getElementById('dashRecentList');
    if (!txs || txs.length === 0) {
        el.innerHTML = '<p class="empty-text">No transactions yet. Go to Analyze to start!</p>';
        return;
    }
    const catEmojis = {
        food_delivery:'🍔', gaming:'🎮', online_shopping:'🛒', entertainment:'🎬',
        alcohol:'🍺', clothing:'👕', electronics:'📱', subscriptions:'📺',
        groceries:'🥦', utilities:'💡', transport:'🚗', healthcare:'🏥',
        education:'📚', other:'📦'
    };
    el.innerHTML = txs.map(t => {
        const cancelled = t.was_cancelled;
        const risk = t.risk_level || 'low';
        return `<div class="recent-item ${cancelled ? 'recent-cancelled' : ''}">
            <div class="recent-left">
                <div class="recent-icon ${risk}">${catEmojis[t.category] || '📦'}</div>
                <div class="recent-info">
                    <span class="recent-merchant">${t.merchant}${cancelled ? ' (Saved ✅)' : ''}</span>
                    <span class="recent-cat">${t.category.replace('_',' ')} · ${new Date(t.timestamp).toLocaleString()}</span>
                </div>
            </div>
            <div class="recent-right">
                <div class="recent-amount">${cancelled ? '+ ' : ''}₹${t.amount.toLocaleString()}</div>
                <div class="recent-score">Score: ${t.impulse_score?.toFixed(0) || 0}</div>
            </div>
        </div>`;
    }).join('');
}

// ─── Goals Form ───
document.getElementById('goalForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = document.getElementById('goalName').value.trim();
    const target = parseFloat(document.getElementById('goalTarget').value);
    if (!name || !target) return;
    try {
        const res = await fetch('/api/dashboard/savings-goal', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, target_amount: target })
        });
        const data = await res.json();
        if (data.status === 'created') {
            showToast('🎯 Savings goal created!', 'success');
            document.getElementById('goalForm').reset();
            loadDashboard();
        }
    } catch (e) { showToast('Error adding goal', 'error'); }
});

// ─── Contacts Form ───
document.getElementById('contactForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = document.getElementById('contactName').value.trim();
    const phone = document.getElementById('contactPhone').value.trim();
    if (!name) return;
    try {
        const res = await fetch('/api/dashboard/accountability-contact', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, phone })
        });
        const data = await res.json();
        if (data.status === 'added') {
            showToast('👥 Accountability contact added!', 'success');
            document.getElementById('contactForm').reset();
            loadDashboard();
        }
    } catch (e) { showToast('Error adding contact', 'error'); }
});

// ─── Seed Demo Data ───
async function loadDemoData() {
    if (!confirm('This will replace your current data with 30 days of realistic demo data. Continue?')) return;
    showToast('📦 Generating demo data...', 'info', 5000);
    try {
        const res = await fetch('/api/seed-demo', { method: 'POST' });
        const data = await res.json();
        if (data.status === 'seeded') {
            showToast(`✅ Loaded ${data.transactions} transactions & ${data.moods} moods!`, 'success', 4000);
            loadDashboard();
        }
    } catch (e) { showToast('Error seeding data', 'error'); }
}

// ─── Clear Data ───
async function clearAllData() {
    if (!confirm('Are you sure? This will delete ALL your transaction, mood, and goal data.')) return;
    try {
        const res = await fetch('/api/dashboard/clear-data', { method: 'POST' });
        const data = await res.json();
        if (data.status === 'cleared') {
            showToast('🗑️ All data cleared!', 'success');
            loadDashboard();
        }
    } catch (e) { showToast('Error clearing data', 'error'); }
}
