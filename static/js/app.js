/**
 * VibeShield v2.0 — Enhanced Transaction Flow
 * Smart item detection, multi-step dopamine lock, settings, deep interconnection
 */

let currentAnalysis = null;
let lockTimer = null;
let lockStartTime = null;
let userSettings = { lock_duration: 20, lock_sensitivity: 'medium', enable_accountability: true, enable_breathing: true, enable_mood_alerts: true };
let smartDetectTimeout = null;

// ─── Item-to-Category Mapping (Client-Side for instant detection) ───
const ITEM_CATEGORIES = {
    'pizza': 'food_delivery', 'burger': 'food_delivery', 'biryani': 'food_delivery',
    'sushi': 'food_delivery', 'noodles': 'food_delivery', 'fries': 'food_delivery',
    'cake': 'food_delivery', 'ice cream': 'food_delivery', 'coffee': 'food_delivery',
    'tea': 'food_delivery', 'sandwich': 'food_delivery', 'wings': 'food_delivery',
    'pasta': 'food_delivery', 'dosa': 'food_delivery', 'paneer': 'food_delivery',
    'momos': 'food_delivery', 'rolls': 'food_delivery', 'smoothie': 'food_delivery',
    'juice': 'food_delivery', 'snack': 'food_delivery', 'chips': 'food_delivery',
    'chocolate': 'food_delivery', 'dessert': 'food_delivery', 'ramen': 'food_delivery',
    'shawarma': 'food_delivery', 'kebab': 'food_delivery', 'thali': 'food_delivery',
    'game': 'gaming', 'ps5': 'gaming', 'xbox': 'gaming', 'steam': 'gaming',
    'controller': 'gaming', 'valorant': 'gaming', 'v-bucks': 'gaming',
    'minecraft': 'gaming', 'fortnite': 'gaming', 'pubg': 'gaming',
    'nintendo': 'gaming', 'playstation': 'gaming', 'console': 'gaming',
    'laptop': 'electronics', 'phone': 'electronics', 'tablet': 'electronics',
    'ipad': 'electronics', 'macbook': 'electronics', 'airpods': 'electronics',
    'earphones': 'electronics', 'headphones': 'electronics', 'charger': 'electronics',
    'mouse': 'electronics', 'keyboard': 'electronics', 'monitor': 'electronics',
    'watch': 'electronics', 'smartwatch': 'electronics', 'camera': 'electronics',
    'speaker': 'electronics', 'tv': 'electronics', 'iphone': 'electronics',
    'samsung': 'electronics', 'powerbank': 'electronics', 'drone': 'electronics',
    'shirt': 'clothing', 'shoes': 'clothing', 'sneakers': 'clothing',
    'dress': 'clothing', 'jacket': 'clothing', 'jeans': 'clothing',
    'hoodie': 'clothing', 't-shirt': 'clothing', 'tshirt': 'clothing',
    'bag': 'clothing', 'backpack': 'clothing', 'sunglasses': 'clothing',
    'perfume': 'clothing', 'belt': 'clothing', 'wallet': 'clothing',
    'saree': 'clothing', 'kurta': 'clothing', 'boots': 'clothing',
    'movie': 'entertainment', 'netflix': 'entertainment', 'concert': 'entertainment',
    'ticket': 'entertainment', 'spotify': 'entertainment', 'disney': 'entertainment',
    'hotstar': 'entertainment', 'show': 'entertainment', 'theatre': 'entertainment',
    'beer': 'alcohol', 'wine': 'alcohol', 'whiskey': 'alcohol', 'vodka': 'alcohol',
    'rum': 'alcohol', 'cocktail': 'alcohol', 'gin': 'alcohol', 'tequila': 'alcohol',
    'subscription': 'subscriptions', 'premium': 'subscriptions', 'membership': 'subscriptions',
    'vegetables': 'groceries', 'fruits': 'groceries', 'milk': 'groceries',
    'bread': 'groceries', 'rice': 'groceries', 'eggs': 'groceries',
    'chicken': 'groceries', 'oil': 'groceries', 'flour': 'groceries',
    'uber': 'transport', 'ola': 'transport', 'cab': 'transport',
    'metro': 'transport', 'fuel': 'transport', 'petrol': 'transport',
    'flight': 'transport', 'train': 'transport',
    'medicine': 'healthcare', 'doctor': 'healthcare', 'pharmacy': 'healthcare',
    'gym': 'healthcare', 'vitamin': 'healthcare',
    'book': 'education', 'course': 'education', 'udemy': 'education',
    'tuition': 'education', 'textbook': 'education',
    'electricity': 'utilities', 'wifi': 'utilities', 'internet': 'utilities',
    'recharge': 'utilities', 'bill': 'utilities',
    'amazon': 'online_shopping', 'flipkart': 'online_shopping', 'myntra': 'online_shopping',
    'meesho': 'online_shopping', 'ajio': 'online_shopping', 'nykaa': 'online_shopping',
};

const CAT_EMOJIS = {
    food_delivery: '🍔', gaming: '🎮', online_shopping: '🛒', entertainment: '🎬',
    alcohol: '🍺', clothing: '👕', electronics: '📱', subscriptions: '📺',
    groceries: '🥦', utilities: '💡', transport: '🚗', healthcare: '🏥',
    education: '📚', other: '📦'
};

const CAT_NAMES = {
    food_delivery: 'Food Delivery', gaming: 'Gaming', online_shopping: 'Online Shopping',
    entertainment: 'Entertainment', alcohol: 'Alcohol', clothing: 'Clothing',
    electronics: 'Electronics', subscriptions: 'Subscriptions', groceries: 'Groceries',
    utilities: 'Utilities', transport: 'Transport', healthcare: 'Healthcare',
    education: 'Education', other: 'Other'
};

// ─── Popular Merchants List ───
const MERCHANTS = [
    { name: 'Swiggy', cat: 'food_delivery', emoji: '🍔' },
    { name: 'Zomato', cat: 'food_delivery', emoji: '🍔' },
    { name: 'Dominos', cat: 'food_delivery', emoji: '🍕' },
    { name: 'McDonald\'s', cat: 'food_delivery', emoji: '🍔' },
    { name: 'KFC', cat: 'food_delivery', emoji: '🍗' },
    { name: 'Pizza Hut', cat: 'food_delivery', emoji: '🍕' },
    { name: 'Subway', cat: 'food_delivery', emoji: '🥪' },
    { name: 'Starbucks', cat: 'food_delivery', emoji: '☕' },
    { name: 'Burger King', cat: 'food_delivery', emoji: '🍔' },
    { name: 'Blinkit', cat: 'groceries', emoji: '🥦' },
    { name: 'Zepto', cat: 'groceries', emoji: '🥦' },
    { name: 'BigBasket', cat: 'groceries', emoji: '🥦' },
    { name: 'Instamart', cat: 'groceries', emoji: '🛒' },
    { name: 'DMart', cat: 'groceries', emoji: '🛒' },
    { name: 'Amazon', cat: 'online_shopping', emoji: '📦' },
    { name: 'Flipkart', cat: 'online_shopping', emoji: '🛒' },
    { name: 'Myntra', cat: 'clothing', emoji: '👕' },
    { name: 'Ajio', cat: 'clothing', emoji: '👗' },
    { name: 'Meesho', cat: 'online_shopping', emoji: '🛍️' },
    { name: 'Nykaa', cat: 'online_shopping', emoji: '💄' },
    { name: 'Tata CLiQ', cat: 'online_shopping', emoji: '🛒' },
    { name: 'Snapdeal', cat: 'online_shopping', emoji: '🛒' },
    { name: 'Croma', cat: 'electronics', emoji: '📱' },
    { name: 'Reliance Digital', cat: 'electronics', emoji: '📱' },
    { name: 'Apple Store', cat: 'electronics', emoji: '🍎' },
    { name: 'Samsung Store', cat: 'electronics', emoji: '📱' },
    { name: 'Netflix', cat: 'entertainment', emoji: '🎬' },
    { name: 'Disney+ Hotstar', cat: 'entertainment', emoji: '🎬' },
    { name: 'Amazon Prime', cat: 'entertainment', emoji: '🎬' },
    { name: 'Spotify', cat: 'entertainment', emoji: '🎵' },
    { name: 'YouTube Premium', cat: 'subscriptions', emoji: '📺' },
    { name: 'JioCinema', cat: 'entertainment', emoji: '🎬' },
    { name: 'SonyLIV', cat: 'entertainment', emoji: '🎬' },
    { name: 'Steam', cat: 'gaming', emoji: '🎮' },
    { name: 'Epic Games', cat: 'gaming', emoji: '🎮' },
    { name: 'PlayStation Store', cat: 'gaming', emoji: '🎮' },
    { name: 'Xbox Store', cat: 'gaming', emoji: '🎮' },
    { name: 'Uber', cat: 'transport', emoji: '🚗' },
    { name: 'Ola', cat: 'transport', emoji: '🚗' },
    { name: 'Rapido', cat: 'transport', emoji: '🏍️' },
    { name: 'IRCTC', cat: 'transport', emoji: '🚆' },
    { name: 'MakeMyTrip', cat: 'transport', emoji: '✈️' },
    { name: 'Goibibo', cat: 'transport', emoji: '✈️' },
    { name: 'EaseMyTrip', cat: 'transport', emoji: '✈️' },
    { name: 'RedBus', cat: 'transport', emoji: '🚌' },
    { name: 'BookMyShow', cat: 'entertainment', emoji: '🎬' },
    { name: 'PVR INOX', cat: 'entertainment', emoji: '🎬' },
    { name: 'PharmEasy', cat: 'healthcare', emoji: '💊' },
    { name: '1mg', cat: 'healthcare', emoji: '💊' },
    { name: 'Netmeds', cat: 'healthcare', emoji: '💊' },
    { name: 'Apollo Pharmacy', cat: 'healthcare', emoji: '🏥' },
    { name: 'Cult.fit', cat: 'healthcare', emoji: '💪' },
    { name: 'Udemy', cat: 'education', emoji: '📚' },
    { name: 'Coursera', cat: 'education', emoji: '📚' },
    { name: 'Unacademy', cat: 'education', emoji: '📚' },
    { name: 'BYJU\'S', cat: 'education', emoji: '📚' },
    { name: 'Jio Recharge', cat: 'utilities', emoji: '📱' },
    { name: 'Airtel', cat: 'utilities', emoji: '📱' },
    { name: 'Vi Recharge', cat: 'utilities', emoji: '📱' },
    { name: 'Electricity Bill', cat: 'utilities', emoji: '💡' },
    { name: 'Water Bill', cat: 'utilities', emoji: '💧' },
    { name: 'Gas Bill', cat: 'utilities', emoji: '🔥' },
    { name: 'Dineout', cat: 'food_delivery', emoji: '🍽️' },
    { name: 'EatSure', cat: 'food_delivery', emoji: '🍔' },
    { name: 'Lenskart', cat: 'online_shopping', emoji: '👓' },
    { name: 'Bewakoof', cat: 'clothing', emoji: '👕' },
    { name: 'H&M', cat: 'clothing', emoji: '👕' },
    { name: 'Zara', cat: 'clothing', emoji: '👗' },
    { name: 'Nike', cat: 'clothing', emoji: '👟' },
    { name: 'Adidas', cat: 'clothing', emoji: '👟' },
    { name: 'Puma', cat: 'clothing', emoji: '👟' },
    { name: 'Decathlon', cat: 'clothing', emoji: '🏃' },
    { name: 'IKEA', cat: 'online_shopping', emoji: '🏠' },
    { name: 'Urban Company', cat: 'utilities', emoji: '🔧' },
    { name: 'Dunzo', cat: 'groceries', emoji: '📦' },
    { name: 'Country Delight', cat: 'groceries', emoji: '🥛' },
    { name: 'Liquor Store', cat: 'alcohol', emoji: '🍺' },
    { name: 'Wine Shop', cat: 'alcohol', emoji: '🍷' },
    { name: 'Bar Tab', cat: 'alcohol', emoji: '🍸' },
];

// ─── Merchant Autocomplete ───
const merchantInput = document.getElementById('txMerchant');
const merchantSugBox = document.getElementById('merchantSuggestions');

merchantInput.addEventListener('input', function() {
    const query = this.value.trim().toLowerCase();
    if (query.length < 1) { merchantSugBox.classList.add('hidden'); return; }

    const matches = MERCHANTS.filter(m => m.name.toLowerCase().includes(query));
    if (matches.length === 0) { merchantSugBox.classList.add('hidden'); return; }

    merchantSugBox.innerHTML = matches.slice(0, 6).map(m =>
        `<div class="merchant-sug-item" data-name="${m.name}" data-cat="${m.cat}">
            <span class="ms-emoji">${m.emoji}</span>
            <span class="ms-name">${m.name}</span>
            <span class="ms-cat">${CAT_NAMES[m.cat] || m.cat}</span>
        </div>`
    ).join('');
    merchantSugBox.classList.remove('hidden');
});

merchantSugBox.addEventListener('mousedown', function(e) {
    e.preventDefault(); // Prevent blur from firing before selection
    const item = e.target.closest('.merchant-sug-item');
    if (!item) return;
    merchantInput.value = item.dataset.name;
    const cat = item.dataset.cat;
    if (cat) document.getElementById('txCategory').value = cat;
    merchantSugBox.classList.add('hidden');
});

merchantSugBox.addEventListener('touchstart', function(e) {
    const item = e.target.closest('.merchant-sug-item');
    if (!item) return;
    e.preventDefault(); // Prevent blur from firing before selection
    merchantInput.value = item.dataset.name;
    const cat = item.dataset.cat;
    if (cat) document.getElementById('txCategory').value = cat;
    merchantSugBox.classList.add('hidden');
});

merchantInput.addEventListener('blur', () => {
    setTimeout(() => merchantSugBox.classList.add('hidden'), 200);
});

merchantInput.addEventListener('focus', function() {
    if (this.value.trim().length >= 1) this.dispatchEvent(new Event('input'));
});

// ─── Smart Item Detection ───
document.getElementById('txItem').addEventListener('input', function() {
    const text = this.value.trim().toLowerCase();
    clearTimeout(smartDetectTimeout);
    const resultEl = document.getElementById('smartDetectResult');
    const suggestEl = document.getElementById('smartSuggestions');

    if (!text || text.length < 2) {
        resultEl.classList.add('hidden');
        suggestEl.classList.add('hidden');
        return;
    }

    smartDetectTimeout = setTimeout(() => {
        const matches = [];
        for (const [item, cat] of Object.entries(ITEM_CATEGORIES)) {
            if (item.includes(text) || text.includes(item)) {
                matches.push({ item, cat });
            }
        }

        if (matches.length > 0) {
            const best = matches[0];
            document.getElementById('txCategory').value = best.cat;
            resultEl.classList.remove('hidden');
            document.getElementById('detectText').textContent =
                `${CAT_EMOJIS[best.cat] || '📦'} ${CAT_NAMES[best.cat] || best.cat}`;

            if (matches.length > 1) {
                const uniqueCats = [...new Set(matches.map(m => m.cat))];
                if (uniqueCats.length > 1) {
                    suggestEl.innerHTML = uniqueCats.slice(0, 4).map(cat =>
                        `<div class="smart-suggestion-item" onclick="selectSmartCategory('${cat}')">
                            <span>${CAT_EMOJIS[cat] || '📦'}</span>
                            <span>${CAT_NAMES[cat] || cat}</span>
                            <span class="sg-cat">Click to select</span>
                        </div>`
                    ).join('');
                    suggestEl.classList.remove('hidden');
                } else {
                    suggestEl.classList.add('hidden');
                }
            } else {
                suggestEl.classList.add('hidden');
            }
        } else {
            resultEl.classList.add('hidden');
            suggestEl.classList.add('hidden');
        }
    }, 200);
});

document.addEventListener('click', (e) => {
    if (!e.target.closest('.smart-input-group')) {
        document.getElementById('smartSuggestions').classList.add('hidden');
    }
});

function selectSmartCategory(cat) {
    document.getElementById('txCategory').value = cat;
    const resultEl = document.getElementById('smartDetectResult');
    resultEl.classList.remove('hidden');
    document.getElementById('detectText').textContent =
        `${CAT_EMOJIS[cat] || '📦'} ${CAT_NAMES[cat] || cat}`;
    document.getElementById('smartSuggestions').classList.add('hidden');
    showToast(`Category set to ${CAT_NAMES[cat]}`, 'success', 1500);
}

// ─── Demo Buttons ───
function fillDemo(merchant, category, amount, hour, dayOfWeek, item) {
    document.getElementById('txAmount').value = amount;
    document.getElementById('txMerchant').value = merchant;
    document.getElementById('txCategory').value = category;
    if (item) document.getElementById('txItem').value = item;

    const now = new Date();
    const demoDate = new Date(now);
    const currentDay = demoDate.getDay();
    const targetDay = dayOfWeek;
    const diff = targetDay - currentDay;
    demoDate.setDate(demoDate.getDate() + (diff <= 0 ? diff : diff - 7));
    demoDate.setHours(hour, Math.floor(Math.random() * 40) + 10, 0, 0);
    document.getElementById('txForm').dataset.simulatedTs = demoDate.toISOString();

    if (item) {
        const cat = ITEM_CATEGORIES[item.toLowerCase()];
        if (cat) {
            const resultEl = document.getElementById('smartDetectResult');
            resultEl.classList.remove('hidden');
            document.getElementById('detectText').textContent =
                `${CAT_EMOJIS[cat] || '📦'} ${CAT_NAMES[cat] || cat}`;
        }
    }

    showToast(`Demo loaded: ${merchant} at ${hour}:00 — click Analyze!`, 'info');
}

// ─── Form Submit ───
document.getElementById('txForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const amount = parseFloat(document.getElementById('txAmount').value);
    const merchant = document.getElementById('txMerchant').value.trim();
    const category = document.getElementById('txCategory').value;

    if (!amount || !merchant || !category) {
        showToast('Please fill in all fields', 'warning');
        return;
    }

    const btn = document.getElementById('analyzeBtn');
    btn.disabled = true;
    btn.textContent = '⏳ Analyzing...';

    const simTs = document.getElementById('txForm').dataset.simulatedTs || null;
    const timestamp = simTs || new Date().toISOString();

    try {
        const res = await fetch('/api/transactions/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ amount, merchant, category, timestamp })
        });
        const data = await res.json();
        if (data.error) {
            showToast(data.error, 'error');
            return;
        }
        currentAnalysis = data;
        displayScore(data);

        if (data.should_lock) {
            setTimeout(() => startDopamineLock(data), 800);
        }
    } catch (err) {
        showToast('Analysis failed: ' + err.message, 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = '🔍 Analyze Impulse Risk';
        delete document.getElementById('txForm').dataset.simulatedTs;
    }
});

// ─── Display Score Card ───
function displayScore(data) {
    document.getElementById('emptyState').classList.add('hidden');
    const card = document.getElementById('scoreCard');
    card.classList.remove('hidden');

    animateGauge(data.impulse_score);

    const badge = document.getElementById('riskBadge');
    badge.textContent = data.risk_level.toUpperCase() + ' RISK';
    badge.className = 'risk-badge risk-' + data.risk_level;

    const td = data.transaction_data;
    document.getElementById('txDetail').innerHTML =
        `<strong>${td.merchant}</strong> · ${td.category.replace('_', ' ')} · ₹${td.amount.toLocaleString()}<br>` +
        `Threshold: ${data.lock_threshold} · ${data.should_lock ? '🔒 Lock triggered' : '✅ No lock needed'}` +
        (data.ml_probability !== null ? `<br>ML confidence: ${(data.ml_probability * 100).toFixed(0)}%` : '');

    renderConnectedInsights(data);

    const grid = document.getElementById('factorsGrid');
    grid.innerHTML = '';
    for (const [key, f] of Object.entries(data.factors)) {
        const pct = (f.score * 100).toFixed(0);
        const color = f.score >= 0.7 ? 'var(--red)' : f.score >= 0.4 ? 'var(--orange)' : 'var(--green)';
        grid.innerHTML += `
            <div class="factor-item" style="border-left-color:${color}">
                <div class="factor-header">
                    <span class="factor-name">${f.label || key.replace(/_/g,' ')}</span>
                    <span class="factor-score" style="color:${color}">${pct}%</span>
                </div>
                <div class="factor-bar"><div class="factor-fill" style="width:${pct}%;background:${color}"></div></div>
                <div class="factor-detail">${f.detail} · weight: ${f.weight}%</div>
            </div>`;
    }

    document.getElementById('aiMessage').innerHTML = '🤖 <strong>AI Interceptor:</strong> ' + data.ai_message;

    document.getElementById('regretBox').innerHTML = data.regret ?
        `<strong>${data.regret.level === 'high' ? '⚠️' : data.regret.level === 'medium' ? '🔶' : '✅'} Regret Prediction</strong><br>${data.regret.message}` : '';
    document.getElementById('savingsBox').innerHTML = data.savings_impact ?
        `<strong>🎯 Savings Impact</strong><br>${data.savings_impact}` : '';

    const accEl = document.getElementById('accountabilityAlert');
    if (data.accountability_alert) {
        accEl.textContent = data.accountability_alert;
        accEl.classList.remove('hidden');
    } else {
        accEl.classList.add('hidden');
    }

    document.getElementById('actionButtons').classList.toggle('hidden', data.should_lock);

    // Scroll to results — use timeout so DOM updates first, with offset for navbar
    setTimeout(() => {
        const navbar = document.querySelector('.navbar');
        const navH = navbar ? navbar.offsetHeight : 60;
        const cardTop = card.getBoundingClientRect().top + window.pageYOffset - navH - 12;
        window.scrollTo({ top: cardTop, behavior: 'smooth' });
    }, 100);
}

// ─── Connected Insights (Deep Interconnection) ───
function renderConnectedInsights(data) {
    const container = document.getElementById('connectedInsights');
    container.innerHTML = '';
    const ctx = data.user_context || {};

    if (ctx.mood_status) {
        const m = ctx.mood_status;
        container.innerHTML += `
            <div class="connected-insight mood-link">
                <span class="ci-emoji">${m.emoji}</span>
                <span class="ci-text">Mood: ${m.mood} · affects risk scoring</span>
            </div>`;
    }
    if (ctx.active_goal) {
        const g = ctx.active_goal;
        container.innerHTML += `
            <div class="connected-insight goal-link">
                <span class="ci-emoji">🎯</span>
                <span class="ci-text">${g.name}: ${g.progress.toFixed(0)}% funded</span>
            </div>`;
    }
    if (ctx.top_trigger) {
        container.innerHTML += `
            <div class="connected-insight trigger-link">
                <span class="ci-emoji">⚡</span>
                <span class="ci-text">Top trigger: ${ctx.top_trigger.category} (${ctx.top_trigger.count}x)</span>
            </div>`;
    }
    if (ctx.control_streak && ctx.control_streak > 0) {
        container.innerHTML += `
            <div class="connected-insight goal-link">
                <span class="ci-emoji">🔥</span>
                <span class="ci-text">${ctx.control_streak} day control streak!</span>
            </div>`;
    }
}

// ─── Gauge Animation ───
function animateGauge(score) {
    const ring = document.getElementById('gaugeRing');
    const scoreEl = document.getElementById('gaugeScore');
    const circumference = 2 * Math.PI * 85;

    ring.style.transition = 'none';
    ring.style.strokeDashoffset = circumference;
    scoreEl.textContent = '0';

    requestAnimationFrame(() => {
        requestAnimationFrame(() => {
            const target = circumference * (1 - score / 100);
            ring.style.transition = 'stroke-dashoffset 1.5s cubic-bezier(0.4, 0, 0.2, 1)';
            ring.style.strokeDashoffset = target;

            if (score >= 65) scoreEl.style.color = 'var(--red)';
            else if (score >= 40) scoreEl.style.color = 'var(--orange)';
            else scoreEl.style.color = 'var(--green)';

            animateCounter(scoreEl, 0, score, 1200);
        });
    });
}

function animateCounter(el, from, to, duration) {
    const start = performance.now();
    function update(now) {
        const elapsed = now - start;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        el.textContent = Math.round(from + (to - from) * eased);
        if (progress < 1) requestAnimationFrame(update);
    }
    requestAnimationFrame(update);
}

// ─── Enhanced Multi-Step Dopamine Lock ───
function startDopamineLock(data) {
    const lockEl = document.getElementById('dopamineLock');
    lockEl.classList.remove('hidden');
    document.body.style.overflow = 'hidden'; // Prevent background scroll on mobile
    document.getElementById('lockButtons').classList.add('hidden');

    const questions = data.reflective_questions || [
        { text: data.reflective_question || 'Do you really need this?', phase: 1, type: 'reflect' }
    ];
    const duration = data.lock_duration || userSettings.lock_duration || 20;
    const enableBreathing = data.settings?.enable_breathing !== false;

    const breathContainer = document.getElementById('breathingContainer');
    breathContainer.style.display = enableBreathing ? '' : 'none';

    // Reset phase indicators
    for (let i = 1; i <= 3; i++) {
        document.getElementById('phaseDot' + i).className = 'phase-dot' + (i === 1 ? ' active' : '');
    }
    document.getElementById('phaseLine1').className = 'phase-line';
    document.getElementById('phaseLine2').className = 'phase-line';

    const questionEl = document.getElementById('lockQuestion');
    const phaseLabel = document.getElementById('lockPhaseLabel');
    const phaseLabels = ['Phase 1: Reflect', 'Phase 2: Connect', 'Phase 3: Decide'];
    let currentPhaseIdx = 0;

    phaseLabel.textContent = phaseLabels[0];
    questionEl.textContent = `"${questions[0].text}"`;
    questionEl.classList.add('lock-question-fade');

    lockStartTime = Date.now();
    let remaining = duration;
    const timerText = document.getElementById('timerText');
    const timerFill = document.getElementById('timerFill');
    timerFill.style.transition = 'none';
    timerFill.style.width = '0%';
    timerText.textContent = remaining + 's';

    const breathText = document.getElementById('breathText');
    let breathPhase = 0;
    const breathCycle = () => {
        if (enableBreathing) {
            breathText.textContent = breathPhase % 2 === 0 ? 'Breathe In...' : 'Breathe Out...';
            breathPhase++;
        }
    };
    breathCycle();
    const breathInterval = setInterval(breathCycle, 3000);

    const phase2Time = Math.floor(duration * 0.33);
    const phase3Time = Math.floor(duration * 0.66);

    lockTimer = setInterval(() => {
        remaining--;
        const pct = ((duration - remaining) / duration * 100).toFixed(1);
        timerFill.style.transition = 'width 1s linear';
        timerFill.style.width = pct + '%';
        timerText.textContent = remaining + 's';

        const elapsed = duration - remaining;
        if (elapsed >= phase2Time && currentPhaseIdx === 0 && questions.length > 1) {
            currentPhaseIdx = 1;
            transitionPhase(2, questions[1].text, phaseLabels[1]);
        }
        if (elapsed >= phase3Time && currentPhaseIdx === 1 && questions.length > 2) {
            currentPhaseIdx = 2;
            transitionPhase(3, questions[2].text, phaseLabels[2]);
        }

        if (remaining <= 0) {
            clearInterval(lockTimer);
            clearInterval(breathInterval);
            timerText.textContent = '0s';
            timerFill.style.width = '100%';
            breathText.textContent = 'Time to decide';
            phaseLabel.textContent = '✨ Make your choice';

            for (let i = 1; i <= 3; i++) {
                document.getElementById('phaseDot' + i).className = 'phase-dot done';
            }
            document.getElementById('phaseLine1').className = 'phase-line filled';
            document.getElementById('phaseLine2').className = 'phase-line filled';

            document.getElementById('lockButtons').classList.remove('hidden');
            // On mobile, scroll lock content so buttons are visible
            setTimeout(() => {
                const btns = document.getElementById('lockButtons');
                btns.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }, 100);
        }
    }, 1000);
}

function transitionPhase(phaseNum, questionText, label) {
    const questionEl = document.getElementById('lockQuestion');
    const phaseLabel = document.getElementById('lockPhaseLabel');

    for (let i = 1; i < phaseNum; i++) {
        document.getElementById('phaseDot' + i).className = 'phase-dot done';
    }
    document.getElementById('phaseDot' + phaseNum).className = 'phase-dot active';
    if (phaseNum >= 2) document.getElementById('phaseLine1').className = 'phase-line filled';
    if (phaseNum >= 3) document.getElementById('phaseLine2').className = 'phase-line filled';

    questionEl.style.opacity = '0';
    setTimeout(() => {
        phaseLabel.textContent = label;
        questionEl.textContent = `"${questionText}"`;
        questionEl.style.opacity = '1';
        questionEl.classList.remove('lock-question-fade');
        void questionEl.offsetWidth;
        questionEl.classList.add('lock-question-fade');
    }, 300);
}

function overrideLock() {
    closeLock();
    commitTransaction();
}

function cancelFromLock() {
    closeLock();
    cancelTransaction();
}

function closeLock() {
    if (lockTimer) clearInterval(lockTimer);
    document.getElementById('dopamineLock').classList.add('hidden');
    document.body.style.overflow = ''; // Restore scroll
    document.getElementById('actionButtons').classList.remove('hidden');
}

// ─── Commit Transaction ───
async function commitTransaction() {
    if (!currentAnalysis) return;
    const td = currentAnalysis.transaction_data;
    try {
        const res = await fetch('/api/transactions/commit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                amount: td.amount, merchant: td.merchant,
                category: td.category, timestamp: td.timestamp
            })
        });
        const data = await res.json();
        if (data.status === 'committed') {
            showToast(`💳 ₹${td.amount.toLocaleString()} committed to ${td.merchant}`, 'warning', 3000);
            resetForm();
            loadRecent();
            loadUserContext();
        }
    } catch (err) {
        showToast('Error committing: ' + err.message, 'error');
    }
}

// ─── Cancel Transaction ───
async function cancelTransaction() {
    if (!currentAnalysis) return;
    const td = currentAnalysis.transaction_data;
    try {
        const res = await fetch('/api/transactions/cancel', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                amount: td.amount, merchant: td.merchant,
                category: td.category, timestamp: td.timestamp
            })
        });
        const data = await res.json();
        if (data.status === 'cancelled') {
            showCelebration(td.amount, data.goal_credited);
            resetForm();
            loadRecent();
            loadUserContext();
        }
    } catch (err) {
        showToast('Error cancelling: ' + err.message, 'error');
    }
}

// ─── Celebration ───
function showCelebration(amount, goalName) {
    const el = document.getElementById('celebration');
    el.classList.remove('hidden');
    document.body.style.overflow = 'hidden'; // Prevent background scroll
    document.getElementById('celebrationTitle').textContent = '🛡️ Impulse Defeated!';
    let msg = `You just saved <strong>₹${amount.toLocaleString()}</strong>!`;
    if (goalName) msg += `<br>Credited to your goal: <strong>${goalName}</strong>`;
    msg += '<br><br>Your future self thanks you. 💪';
    document.getElementById('celebrationMsg').innerHTML = msg;
}

function closeCelebration() {
    document.getElementById('celebration').classList.add('hidden');
    document.body.style.overflow = ''; // Restore scroll
    // Scroll back to top/form on mobile
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ─── Reset Form ───
function resetForm() {
    document.getElementById('txForm').reset();
    document.getElementById('scoreCard').classList.add('hidden');
    document.getElementById('emptyState').classList.remove('hidden');
    document.getElementById('smartDetectResult').classList.add('hidden');
    document.getElementById('smartSuggestions').classList.add('hidden');
    currentAnalysis = null;
    const ring = document.getElementById('gaugeRing');
    ring.style.transition = 'none';
    ring.style.strokeDashoffset = 534.07;
}

// ─── Load Recent Transactions ───
async function loadRecent() {
    try {
        const res = await fetch('/api/transactions/recent');
        const data = await res.json();
        const el = document.getElementById('recentList');
        if (!data.transactions || data.transactions.length === 0) {
            el.innerHTML = '<p class="empty-text">No transactions yet. Start by analyzing one above!</p>';
            return;
        }
        el.innerHTML = data.transactions.map(t => {
            const cancelled = t.was_cancelled;
            const risk = t.risk_level || 'low';
            const emoji = CAT_EMOJIS[t.category] || '📦';
            return `
                <div class="recent-item ${cancelled ? 'recent-cancelled' : ''}">
                    <div class="recent-left">
                        <div class="recent-icon ${risk}">${emoji}</div>
                        <div class="recent-info">
                            <span class="recent-merchant">${t.merchant}${cancelled ? ' (Cancelled ✅)' : ''}</span>
                            <span class="recent-cat">${t.category.replace('_',' ')} · ${new Date(t.timestamp).toLocaleString()}</span>
                        </div>
                    </div>
                    <div class="recent-right">
                        <div class="recent-amount">₹${t.amount.toLocaleString()}</div>
                        <div class="recent-score">Score: ${t.impulse_score?.toFixed(0) || 0}</div>
                    </div>
                </div>`;
        }).join('');
    } catch (e) { console.error(e); }
}

// ─── User Context Bar (Deep Interconnection) ───
async function loadUserContext() {
    try {
        const res = await fetch('/api/transactions/context');
        const ctx = await res.json();

        const moodEl = document.getElementById('ctxMood');
        if (ctx.mood_status) {
            const m = ctx.mood_status;
            moodEl.querySelector('.ctx-emoji').textContent = m.emoji;
            moodEl.querySelector('.ctx-text').textContent = `${m.mood}`;
            moodEl.title = `Current mood: ${m.mood} (intensity ${m.intensity}/10)`;
        }

        const goalEl = document.getElementById('ctxGoal');
        if (ctx.active_goal) {
            const g = ctx.active_goal;
            goalEl.querySelector('.ctx-text').textContent = `${g.name}: ${g.progress.toFixed(0)}%`;
            goalEl.title = `${g.name}: ₹${g.current.toLocaleString()} / ₹${g.target.toLocaleString()}`;
        }

        const streakEl = document.getElementById('ctxStreak');
        if (ctx.control_streak !== undefined) {
            streakEl.querySelector('.ctx-text').textContent = `${ctx.control_streak}d streak`;
            streakEl.title = `${ctx.control_streak} day control streak`;
        }
    } catch (e) { console.error('Context load error:', e); }
}

// ─── Settings ───
function toggleSettings() {
    const modal = document.getElementById('settingsModal');
    modal.classList.toggle('hidden');
    // Prevent body scroll when settings modal is open on mobile
    document.body.style.overflow = modal.classList.contains('hidden') ? '' : 'hidden';
}

async function loadSettings() {
    try {
        const res = await fetch('/api/transactions/settings');
        const data = await res.json();
        if (data.lock_duration) {
            userSettings = {
                lock_duration: data.lock_duration,
                lock_sensitivity: data.lock_sensitivity || 'medium',
                enable_accountability: !!data.enable_accountability,
                enable_breathing: !!data.enable_breathing,
                enable_mood_alerts: !!data.enable_mood_alerts,
            };
        }
        document.querySelectorAll('#lockDurationOptions .setting-opt').forEach(btn => {
            btn.classList.toggle('active', parseInt(btn.dataset.val) === userSettings.lock_duration);
        });
        document.querySelectorAll('#sensitivityOptions .setting-opt').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.val === userSettings.lock_sensitivity);
        });
        document.getElementById('settingBreathing').checked = userSettings.enable_breathing;
        document.getElementById('settingAccountability').checked = userSettings.enable_accountability;
        document.getElementById('settingMoodAlerts').checked = userSettings.enable_mood_alerts;
    } catch (e) { console.error('Settings load error:', e); }
}

function setLockDuration(val) {
    userSettings.lock_duration = val;
    document.querySelectorAll('#lockDurationOptions .setting-opt').forEach(btn => {
        btn.classList.toggle('active', parseInt(btn.dataset.val) === val);
    });
    saveSettings();
}

function setSensitivity(val) {
    userSettings.lock_sensitivity = val;
    document.querySelectorAll('#sensitivityOptions .setting-opt').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.val === val);
    });
    saveSettings();
}

async function saveSettings() {
    userSettings.enable_breathing = document.getElementById('settingBreathing').checked;
    userSettings.enable_accountability = document.getElementById('settingAccountability').checked;
    userSettings.enable_mood_alerts = document.getElementById('settingMoodAlerts').checked;

    try {
        await fetch('/api/transactions/settings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userSettings)
        });
        showToast('Settings saved ✓', 'success', 1500);
    } catch (e) {
        showToast('Failed to save settings', 'error');
    }
}

// ─── Initialize ───
document.addEventListener('DOMContentLoaded', () => {
    loadRecent();
    loadUserContext();
    loadSettings();
});
