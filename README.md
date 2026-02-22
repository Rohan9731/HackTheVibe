<p align="center">
  <img src="https://img.shields.io/badge/VibeShield-v2.0-6c5ce7?style=for-the-badge" alt="VibeShield"/>
</p>

<h1 align="center">🛡️ VibeShield — The Impulse Intelligence Layer</h1>

<p align="center">
  <strong>AI-powered impulse purchase interceptor that analyzes, predicts, and prevents regretful spending in real-time.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.12"/>
  <img src="https://img.shields.io/badge/FastAPI-0.104-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/scikit--learn-1.3-F7931E?style=flat-square&logo=scikit-learn&logoColor=white" alt="scikit-learn"/>
  <img src="https://img.shields.io/badge/Chart.js-4.4-FF6384?style=flat-square&logo=chart.js&logoColor=white" alt="Chart.js"/>
  <img src="https://img.shields.io/badge/SQLite-Per--User-003B57?style=flat-square&logo=sqlite&logoColor=white" alt="SQLite"/>
</p>

---

## 🎯 What is VibeShield?

VibeShield is a behavioral finance tool that acts as an **intelligent layer between you and your impulse purchases**. It uses a 7-factor weighted scoring algorithm + machine learning to calculate an "Impulse Score" for every transaction, then deploys a multi-step **Dopamine Lock** system to create a cooling period before you spend.

> **Core Insight:** Most impulse purchases happen in under 30 seconds. VibeShield creates a frictionful pause — using reflective questions, breathing exercises, and contextual awareness — to break the dopamine loop.

---

## ✨ Key Features

### 🔍 7-Factor Impulse Scoring Engine
Every transaction is analyzed across 7 weighted dimensions:

| Factor | Weight | What it Measures |
|--------|--------|-----------------|
| ⏰ Time of Day | 25% | Late-night purchases score higher risk |
| 🏷️ Category Risk | 15% | Food delivery, gaming, alcohol = high risk |
| 💰 Amount Deviation | 20% | How much this deviates from your average |
| 📈 Frequency Spike | 15% | Multiple purchases in a short window |
| 🧠 Mood Influence | 10% | Current mood → spending correlation |
| 🎯 Goal Conflict | 10% | Does this hurt your active savings goal? |
| 📅 Payday Proximity | 5% | Spending spikes near paydays |

### 🔒 Multi-Step Dopamine Lock
When the impulse score exceeds the threshold, a 3-phase lock activates:
- **Phase 1 — Reflect:** A universal question to pause automatic behavior
- **Phase 2 — Connect:** Context-aware question using your mood, goals, and time
- **Phase 3 — Decide:** Hard-hitting personal question about financial values
- Includes a **guided breathing exercise** (6-second inhale/exhale cycle)
- Configurable duration: 10s / 15s / 20s / 30s / 45s / 60s

### 🤖 Smart Detection System
- **Merchant Autocomplete:** Type any merchant name and get instant dropdown suggestions (75+ Indian merchants — Swiggy, Zomato, Amazon, Flipkart, etc.) with auto-category detection
- **Item Auto-Detect:** Type what you're buying (e.g., "watch" → Electronics, "pizza" → Food Delivery) — 120+ items mapped with client-side instant detection

### 📊 Four Interconnected Modes
All modes share data and feed into each other:

1. **Analyze** — Real-time transaction impulse scoring with AI interceptor messages
2. **Dashboard** — Spending stats, gamification levels, daily/category charts, savings goals, accountability contacts
3. **Trigger Map** — Spending heatmap (time × day), category-by-hour patterns, AI-generated insights
4. **Mood Tracker** — 8-mood check-in with intensity slider, mood-spending correlation charts, mood × impulse risk mapping

### 🔗 Deep Cross-Mode Intelligence
- Context bar on Analyze page shows current mood, active goal, control streak
- Dashboard shows mood status, top trigger, lock sensitivity
- Trigger Map displays live mood, goal progress, savings data
- Mood page shows how each mood maps to impulse risk percentage
- Score card displays connected insights (mood, goal progress, top trigger, streak)

### ⚙️ Personalization
- Configurable lock duration and sensitivity (High/Medium/Low)
- Toggle breathing exercise, accountability alerts, mood alerts
- Per-user data isolation with cookie-based sessions
- Adaptive thresholds based on sensitivity settings

---

## 🏗️ Architecture

```
HackTheVibe/
├── app/
│   ├── main.py                  # FastAPI app, routes, auth, startup
│   ├── database.py              # SQLite CRUD, per-user isolation, 5 tables
│   ├── models.py                # Pydantic request/response models
│   ├── seed_data.py             # 30-day realistic demo data generator
│   ├── routers/
│   │   ├── transactions.py      # /analyze, /commit, /cancel, /settings, /context
│   │   ├── mood.py              # /checkin, /recent, /correlation
│   │   └── dashboard.py         # /stats, /triggers, /goals, /contacts
│   └── ml/
│       ├── impulse_engine.py    # 7-factor scoring, ML model, smart detect, questions
│       ├── regret_simulator.py  # Regret prediction, savings impact, AI messages
│       ├── trigger_mapper.py    # Heatmap builder, category-by-hour, insights
│       └── mood_correlator.py   # Mood-spending correlation analysis
├── templates/
│   ├── base.html                # Layout: navbar, toast system, CDN imports
│   ├── login.html               # User authentication page
│   ├── index.html               # Analyze page (form, score card, dopamine lock)
│   ├── dashboard.html           # Stats, charts, goals, contacts
│   ├── triggers.html            # Heatmap, category patterns, AI insights
│   └── mood.html                # Mood check-in, history, correlation charts
├── static/
│   ├── css/style.css            # Dark fintech theme (450+ lines)
│   └── js/
│       ├── app.js               # Analyze page logic (780+ lines)
│       └── dashboard.js         # Dashboard charts & stats
├── requirements.txt
├── run.py
└── README.md
```

### Database Schema (SQLite — Per-User Isolation)

| Table | Key Columns |
|-------|-------------|
| `transactions` | user_id, merchant, category, amount, impulse_score, risk_level, was_cancelled, timestamp |
| `moods` | user_id, mood, intensity, notes, timestamp |
| `savings_goals` | user_id, name, target_amount, current_amount |
| `accountability_contacts` | user_id, name, phone |
| `user_settings` | user_id, lock_duration, lock_sensitivity, enable_breathing, enable_accountability, enable_mood_alerts |

---

## 🧠 ML Pipeline

### Rule-Based Scoring (Always Active)
The 7-factor engine produces a score from 0–100 by combining weighted sub-scores. Each factor returns a 0.0–1.0 value based on domain-specific heuristics:
- **Time scoring** uses a gaussian curve peaking at 2 AM (late-night = high risk)
- **Category risk** is a preset dictionary (alcohol: 0.9, gaming: 0.8, groceries: 0.15)
- **Amount deviation** compares to the user's running average using z-score
- **Frequency spike** counts transactions in the last hour
- **Mood influence** maps mood to risk multiplier (angry: 0.95, happy: 0.15)
- **Goal conflict** calculates remaining goal amount vs. purchase amount

### Per-User RandomForest (Activates After 15+ Transactions)
Once a user has enough history, a `RandomForestClassifier` (50 trees, max_depth=5) is trained on their personal spending patterns using features: `[hour, weekday, amount, category_risk]`. The ML probability is shown as a confidence indicator alongside the rule-based score.

### Smart Category Detection
120+ items mapped to 14 categories with both client-side (instant, zero-latency) and server-side (API fallback) detection. Uses exact match → substring match fallback chain.

### Multi-Step Reflective Questions
6 question banks (mood_aware, goal_aware, time_aware, pattern_aware, amount_aware, generic) with template variables. Questions progressively escalate from gentle reflection → context-aware confrontation → hard-hitting personal challenge.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+ installed
- pip package manager

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/your-username/HackTheVibe.git
cd HackTheVibe

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the server
python run.py
```

### Open in Browser
```
http://localhost:8000
```

Enter your name to create a session → start analyzing transactions!

### Try Demo Scenarios
Click any **Quick Demo Scenario** button on the Analyze page:
- 🌙 **1AM Midnight Snack** — Swiggy order at 1 AM (high impulse)
- 🛒 **11PM Shopping Spree** — Amazon headphones at 11 PM (high impulse)
- 🎮 **2AM Gaming Purchase** — Steam game at 2 AM (medium-high impulse)
- 🥦 **10AM Planned Groceries** — BigBasket at 10 AM (low impulse)

Or click **Load 30-Day Demo Data** on the Dashboard for a full dataset with charts.

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend** | FastAPI 0.104 | Async REST API with auto-docs |
| **ML Engine** | scikit-learn 1.3 | RandomForest per-user impulse prediction |
| **Data Processing** | NumPy 1.26 + Pandas 2.1 | Feature engineering, aggregations |
| **Database** | SQLite | Zero-config, per-user isolated data |
| **Templating** | Jinja2 3.1 | Server-side HTML rendering |
| **Validation** | Pydantic 2.5 | Request/response model validation |
| **Frontend** | Vanilla JS + Chart.js 4.4 | Interactive charts, real-time UI |
| **Styling** | Custom CSS | Dark fintech theme, responsive grid |
| **Server** | Uvicorn 0.24 | ASGI server with hot-reload |

---

## 📡 API Endpoints

### Transaction Analysis
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/transactions/analyze` | Analyze a transaction's impulse risk |
| `POST` | `/api/transactions/commit` | Commit (proceed with) a transaction |
| `POST` | `/api/transactions/cancel` | Cancel a transaction and save money |
| `GET` | `/api/transactions/recent` | Get recent transaction history |
| `POST` | `/api/transactions/detect-category` | Auto-detect category from item name |
| `GET` | `/api/transactions/context` | Get cross-mode user context |
| `GET/POST` | `/api/transactions/settings` | Read/update user settings |

### Mood Tracking
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/mood/checkin` | Log a mood check-in |
| `GET` | `/api/mood/recent` | Get mood history |
| `GET` | `/api/mood/correlation` | Get mood-spending correlation data |

### Dashboard
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/dashboard/stats` | Full dashboard stats + charts data |
| `GET` | `/api/dashboard/triggers` | Trigger heatmap + category patterns |
| `POST` | `/api/dashboard/goals` | Add a savings goal |
| `POST` | `/api/dashboard/contacts` | Add an accountability contact |
| `POST` | `/api/dashboard/clear` | Clear all user data |

---

## 🎮 Gamification System

Users earn levels based on cancelled impulse purchases:

| Level | Title | Requirement | Emoji |
|-------|-------|-------------|-------|
| 0 | Just Starting | 0 cancels | 🚀 |
| 1 | Impulse Aware | 2 cancels | 🌱 |
| 2 | Budget Warrior | 5 cancels | ⚔️ |
| 3 | Savings Ninja | 10 cancels | 🥷 |
| 4 | Money Master | 20 cancels | 👑 |
| 5 | VibeShield Legend | 50 cancels | 🏆 |

---

## 🎨 Design Philosophy

- **Dark Fintech Theme:** Deep navy (#0a0a1a) backgrounds with purple (#6c5ce7) accents, designed for extended use without eye strain
- **Friction by Design:** The dopamine lock isn't a bug — it's the core feature. Every delay is intentional
- **Data Flows Everywhere:** No mode operates in isolation. Mood feeds into scoring, triggers feed into dashboard, goals feed into reflective questions
- **Indian Market Focus:** Merchants, currency (₹), and spending patterns optimized for Indian users (Swiggy, Zomato, Amazon, Flipkart, IRCTC, etc.)

---

## 🔒 Privacy & Data

- **No external APIs** — all ML runs locally, no data leaves your machine
- **SQLite file-based database** (`vibeshield.db`) — auto-created on first run
- **Cookie-based sessions** (`vibeshield_user`, `vibeshield_name`) — 24-hour expiry
- **Per-user isolation** — every database query is scoped to the logged-in user
- **All ML models trained in-memory** — no model files stored on disk

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit changes (`git commit -m 'Add your feature'`)
4. Push to branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

## 📄 License

This project is built for **HackTheVibe Hackathon 2026**. Open source under the MIT License.

---

<p align="center">
  Built with 💜 and behavioral science<br/>
  <strong>VibeShield — Because your wallet deserves a bodyguard.</strong>
</p>
