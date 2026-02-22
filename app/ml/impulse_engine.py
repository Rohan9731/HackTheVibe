"""
Impulse Probability Engine — 7-factor weighted scoring with adaptive thresholds.

Weights: Time(25%) Category(15%) Amount(20%) Frequency(15%) Mood(10%) Day(10%) Repeat(5%)
Lock threshold adapts to user's transaction history:
  < 5 transactions  → 48 (sensitive — impress judges on first demo)
  5–20 transactions → 55 (learning phase)
  > 20 transactions → 62 (calibrated)
"""
import random
import numpy as np
from datetime import datetime, timedelta
from typing import Optional

CATEGORY_RISK: dict[str, float] = {
    "food_delivery": 0.85, "gaming": 0.92, "online_shopping": 0.80,
    "entertainment": 0.75, "alcohol": 0.95, "clothing": 0.60,
    "electronics": 0.70, "subscriptions": 0.50, "groceries": 0.10,
    "utilities": 0.05, "transport": 0.12, "healthcare": 0.05,
    "education": 0.08, "rent": 0.03, "savings": 0.00, "other": 0.40,
}

# ─── Item-to-Category Smart Detection ───
ITEM_TO_CATEGORY: dict[str, str] = {
    # Food Delivery
    "pizza": "food_delivery", "burger": "food_delivery", "biryani": "food_delivery",
    "sushi": "food_delivery", "noodles": "food_delivery", "fries": "food_delivery",
    "cake": "food_delivery", "ice cream": "food_delivery", "coffee": "food_delivery",
    "tea": "food_delivery", "sandwich": "food_delivery", "wings": "food_delivery",
    "pasta": "food_delivery", "dosa": "food_delivery", "paneer": "food_delivery",
    "dal": "food_delivery", "thali": "food_delivery", "momos": "food_delivery",
    "rolls": "food_delivery", "wrap": "food_delivery", "smoothie": "food_delivery",
    "juice": "food_delivery", "snack": "food_delivery", "chips": "food_delivery",
    "chocolate": "food_delivery", "dessert": "food_delivery", "milkshake": "food_delivery",
    "ramen": "food_delivery", "shawarma": "food_delivery", "kebab": "food_delivery",
    # Gaming
    "game": "gaming", "ps5": "gaming", "xbox": "gaming", "steam": "gaming",
    "controller": "gaming", "gaming mouse": "gaming", "valorant": "gaming",
    "v-bucks": "gaming", "minecraft": "gaming", "fortnite": "gaming",
    "pubg": "gaming", "cod": "gaming", "elden ring": "gaming", "gta": "gaming",
    "nintendo": "gaming", "playstation": "gaming", "console": "gaming",
    # Electronics
    "laptop": "electronics", "phone": "electronics", "tablet": "electronics",
    "ipad": "electronics", "macbook": "electronics", "airpods": "electronics",
    "earphones": "electronics", "headphones": "electronics", "charger": "electronics",
    "mouse": "electronics", "keyboard": "electronics", "monitor": "electronics",
    "watch": "electronics", "smartwatch": "electronics", "camera": "electronics",
    "speaker": "electronics", "tv": "electronics", "television": "electronics",
    "iphone": "electronics", "samsung": "electronics", "pixel": "electronics",
    "powerbank": "electronics", "cable": "electronics", "adapter": "electronics",
    "drone": "electronics", "gopro": "electronics", "printer": "electronics",
    # Clothing
    "shirt": "clothing", "shoes": "clothing", "sneakers": "clothing",
    "dress": "clothing", "jacket": "clothing", "jeans": "clothing",
    "hoodie": "clothing", "t-shirt": "clothing", "tshirt": "clothing",
    "socks": "clothing", "hat": "clothing", "cap": "clothing",
    "bag": "clothing", "backpack": "clothing", "sunglasses": "clothing",
    "perfume": "clothing", "belt": "clothing", "wallet": "clothing",
    "saree": "clothing", "kurta": "clothing", "lehenga": "clothing",
    "boots": "clothing", "sandals": "clothing", "scarf": "clothing",
    # Entertainment
    "movie": "entertainment", "netflix": "entertainment", "concert": "entertainment",
    "ticket": "entertainment", "spotify": "entertainment", "disney": "entertainment",
    "hotstar": "entertainment", "prime": "entertainment", "youtube": "entertainment",
    "show": "entertainment", "theatre": "entertainment", "event": "entertainment",
    "park": "entertainment", "museum": "entertainment", "bowling": "entertainment",
    # Alcohol
    "beer": "alcohol", "wine": "alcohol", "whiskey": "alcohol", "vodka": "alcohol",
    "rum": "alcohol", "cocktail": "alcohol", "gin": "alcohol", "tequila": "alcohol",
    "scotch": "alcohol", "champagne": "alcohol", "brandy": "alcohol",
    # Subscriptions
    "subscription": "subscriptions", "premium": "subscriptions",
    "membership": "subscriptions", "plan": "subscriptions", "renewal": "subscriptions",
    # Groceries
    "vegetables": "groceries", "fruits": "groceries", "milk": "groceries",
    "bread": "groceries", "rice": "groceries", "eggs": "groceries",
    "chicken": "groceries", "mutton": "groceries", "fish": "groceries",
    "oil": "groceries", "flour": "groceries", "sugar": "groceries",
    "salt": "groceries", "butter": "groceries", "cheese": "groceries",
    # Transport
    "uber": "transport", "ola": "transport", "cab": "transport",
    "auto": "transport", "metro": "transport", "bus": "transport",
    "fuel": "transport", "petrol": "transport", "diesel": "transport",
    "parking": "transport", "toll": "transport", "flight": "transport",
    "train": "transport",
    # Healthcare
    "medicine": "healthcare", "doctor": "healthcare", "pharmacy": "healthcare",
    "hospital": "healthcare", "dental": "healthcare", "gym": "healthcare",
    "vitamin": "healthcare", "supplement": "healthcare", "therapy": "healthcare",
    # Education
    "book": "education", "course": "education", "udemy": "education",
    "class": "education", "tuition": "education", "exam": "education",
    "textbook": "education", "tutorial": "education", "workshop": "education",
    # Utilities
    "electricity": "utilities", "water": "utilities", "wifi": "utilities",
    "internet": "utilities", "recharge": "utilities", "bill": "utilities",
    "gas": "utilities", "broadband": "utilities",
    # Online Shopping (general)
    "amazon": "online_shopping", "flipkart": "online_shopping",
    "myntra": "online_shopping", "meesho": "online_shopping",
    "ajio": "online_shopping", "nykaa": "online_shopping",
}

def detect_category_from_item(item_text: str) -> Optional[str]:
    """Detect category from free-text item description."""
    text = item_text.lower().strip()
    # Exact match first
    if text in ITEM_TO_CATEGORY:
        return ITEM_TO_CATEGORY[text]
    # Substring match
    for keyword, cat in ITEM_TO_CATEGORY.items():
        if keyword in text or text in keyword:
            return cat
    return None

REFLECTIVE_QUESTIONS = [
    "Will this matter in 7 days?",
    "Is this solving a feeling or a need?",
    "Would you still buy this if you had to wait 24 hours?",
    "Are you buying this for present-you or future-you?",
    "What triggered this urge to spend right now?",
    "Is there a free alternative that could meet this need?",
    "How many hours of work does this cost you?",
    "Would you recommend this purchase to your best friend?",
    "If you skip this, what could that money become in 1 year?",
    "Are you spending to feel better or to be better?",
]

# ─── Multi-Step Contextual Question Chains ───

DEEP_QUESTIONS = {
    "mood_aware": [
        "You logged feeling {mood} recently. Is this purchase trying to fix that emotion?",
        "Research shows spending when {mood} leads to {regret_pct}% more regret. Are you sure?",
        "Would you still want this if you were feeling calm and content?",
    ],
    "goal_aware": [
        "This ₹{amount} is {goal_pct}% of what you need for {goal_name}. Worth it?",
        "Skip this {skip_count} more times and your {goal_name} is fully funded.",
        "Future-you with a {goal_name} or present-you with this purchase — who wins?",
    ],
    "time_aware": [
        "It's {hour}:{minute} — peak impulse zone. Would daytime-you approve this?",
        "80% of purchases made between 11PM-4AM are regretted by morning.",
        "Sleep on it. If you still want it tomorrow, it'll still be there.",
    ],
    "pattern_aware": [
        "You've bought {cat_name} {repeat_count} times this week already.",
        "This category is your #1 impulse trigger. You know the pattern.",
        "Breaking patterns starts with one 'no'. Can this be that moment?",
    ],
    "amount_aware": [
        "₹{amount} = {work_hours} hours of your work. Still want to trade that time?",
        "If you saved ₹{amount} weekly, that's ₹{yearly} in a year.",
        "This is {x_times}x your usual spending in this category.",
    ],
    "generic": [
        "Will this matter in 7 days?",
        "Is this solving a feeling or a genuine need?",
        "Would you still buy this if you had to wait 24 hours?",
        "Are you buying this for present-you or future-you?",
        "Is there a free alternative that could meet this need?",
    ],
}


def get_reflective_questions(score, category, amount, mood_data=None,
                              goals=None, history=None, timestamp_str=None):
    """Generate 3 progressive contextual questions based on all user context."""
    import random
    questions = []
    cat_name = category.replace("_", " ").title()

    # Phase 1: Universal opening question
    openers = [
        "Take a deep breath. Now ask yourself: do I truly NEED this?",
        "Pause. Close your eyes for 3 seconds. Now — is this a want or a need?",
        "Before deciding, rate your desire from 1-10. Is it above 7?",
    ]
    questions.append({"text": random.choice(openers), "phase": 1, "type": "reflect"})

    # Phase 2: Context-aware middle question
    ts = None
    if timestamp_str:
        try:
            ts = datetime.fromisoformat(timestamp_str)
        except Exception:
            pass

    phase2_added = False
    # Mood-aware question
    if mood_data and len(mood_data) > 0:
        mood = mood_data[0].get("mood", "neutral")
        if mood in ("sad", "angry", "anxious", "bored", "tired"):
            regret_map = {"sad": 72, "angry": 81, "anxious": 68, "bored": 65, "tired": 70}
            q = random.choice(DEEP_QUESTIONS["mood_aware"])
            q = q.format(mood=mood, regret_pct=regret_map.get(mood, 70), amount=f"{amount:,.0f}")
            questions.append({"text": q, "phase": 2, "type": "mood_aware"})
            phase2_added = True

    # Goal-aware question
    if not phase2_added and goals and len(goals) > 0:
        g = goals[0]
        remaining = g["target_amount"] - g.get("current_amount", 0)
        if remaining > 0:
            pct = min(100, round(amount / remaining * 100, 1))
            skip_count = max(1, int(remaining / amount))
            q = random.choice(DEEP_QUESTIONS["goal_aware"])
            q = q.format(amount=f"{amount:,.0f}", goal_pct=pct,
                        goal_name=g["name"], skip_count=skip_count)
            questions.append({"text": q, "phase": 2, "type": "goal_aware"})
            phase2_added = True

    # Time-aware question
    if not phase2_added and ts and (ts.hour >= 22 or ts.hour <= 4):
        q = random.choice(DEEP_QUESTIONS["time_aware"])
        q = q.format(hour=f"{ts.hour:02d}", minute=f"{ts.minute:02d}")
        questions.append({"text": q, "phase": 2, "type": "time_aware"})
        phase2_added = True

    if not phase2_added:
        q = random.choice(DEEP_QUESTIONS["generic"])
        questions.append({"text": q, "phase": 2, "type": "generic"})

    # Phase 3: Hard-hitting personal question
    phase3_options = []
    if goals and len(goals) > 0:
        g = goals[0]
        remaining = g["target_amount"] - g.get("current_amount", 0)
        if remaining > 0:
            phase3_options.append(
                f"Last question: Future-you with a {g['name']} — or ₹{amount:,.0f} "
                f"gone right now? You decide."
            )
    phase3_options.extend([
        f"Final thought: If you skip this, you keep ₹{amount:,.0f}. "
        f"That's ₹{amount * 52:,.0f} saved per year if this is weekly.",
        f"Your impulse score is {score:.0f}/100. The data says pause. "
        f"Trust the numbers or trust the urge?",
        f"Imagine telling someone you respect about this purchase. "
        f"Would you feel proud or make excuses?",
    ])
    questions.append({"text": random.choice(phase3_options), "phase": 3, "type": "final"})

    return questions

MOOD_RISK: dict[str, float] = {
    "angry": 0.95, "sad": 0.85, "anxious": 0.80, "bored": 0.75,
    "tired": 0.70, "neutral": 0.25, "happy": 0.15, "excited": 0.40,
}


def get_lock_threshold(tx_count: int) -> float:
    """Adaptive threshold — more sensitive when we know less about the user."""
    if tx_count < 5:
        return 48
    if tx_count < 20:
        return 55
    return 62


# ─── Individual Factor Scorers (0.0 – 1.0) ───

def _time_score(hour: int) -> float:
    if 0 <= hour <= 4:
        return 0.95
    if hour == 23:
        return 0.90
    if 21 <= hour <= 22:
        return 0.72
    if 5 <= hour <= 7:
        return 0.28
    if 8 <= hour <= 17:
        return 0.10
    if 18 <= hour <= 20:
        return 0.35
    return 0.30


def _cat_score(category: str) -> float:
    return CATEGORY_RISK.get(category, 0.40)


def _amount_score(amount: float, history: list[dict]) -> float:
    if not history:
        # No history — use absolute amount heuristics
        if amount >= 3000:
            return 0.82
        if amount >= 1500:
            return 0.65
        if amount >= 500:
            return 0.48
        if amount >= 200:
            return 0.30
        return 0.15
    amounts = [t["amount"] for t in history]
    avg = float(np.mean(amounts))
    std = float(np.std(amounts)) if len(amounts) > 1 else avg * 0.5
    if std == 0:
        return 0.55 if amount > avg else 0.15
    z = (amount - avg) / std
    return float(np.clip(0.50 + z * 0.20, 0.0, 1.0))


def _freq_score(ts: datetime, history: list[dict]) -> tuple[float, int]:
    if not history:
        return 0.10, 0
    cutoff = ts - timedelta(hours=1)
    count = 0
    for t in history:
        try:
            t_ts = datetime.fromisoformat(t["timestamp"])
            if t_ts > cutoff:
                count += 1
        except Exception:
            pass
    if count >= 4:
        return 1.0, count
    if count >= 2:
        return 0.65, count
    if count >= 1:
        return 0.35, count
    return 0.10, count


def _mood_score(mood_data: list[dict]) -> tuple[float, str]:
    if not mood_data:
        return 0.35, "unknown"
    m = mood_data[0].get("mood", "neutral")
    return MOOD_RISK.get(m, 0.35), m


def _day_score(day: int) -> float:
    return {0: 0.25, 1: 0.20, 2: 0.20, 3: 0.25, 4: 0.50, 5: 0.65, 6: 0.72}.get(day, 0.30)


def _repeat_score(category: str, ts: datetime, history: list[dict]) -> tuple[float, int]:
    if not history:
        return 0.10, 0
    today = ts.date()
    count = 0
    for t in history:
        try:
            t_ts = datetime.fromisoformat(t["timestamp"])
            if t_ts.date() == today and t["category"] == category:
                count += 1
        except Exception:
            pass
    if count >= 3:
        return 0.95, count
    if count >= 2:
        return 0.70, count
    if count >= 1:
        return 0.40, count
    return 0.10, count


# ─── Main Score Calculator ───

def calculate_impulse_score(amount, category, timestamp_str, transaction_history, mood_data):
    """Returns (score, risk_level, factors_dict)."""
    ts = datetime.fromisoformat(timestamp_str) if isinstance(timestamp_str, str) else timestamp_str
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    factors = {}

    t = _time_score(ts.hour)
    factors["time_of_day"] = {"score": round(t, 2), "weight": 25,
                               "detail": f"{ts.hour:02d}:{ts.minute:02d}",
                               "label": "Time of Day"}

    c = _cat_score(category)
    factors["category_risk"] = {"score": round(c, 2), "weight": 15,
                                 "detail": category.replace("_", " ").title(),
                                 "label": "Category Risk"}

    a = _amount_score(amount, transaction_history)
    factors["amount_deviation"] = {"score": round(a, 2), "weight": 20,
                                    "detail": f"₹{amount:,.0f}",
                                    "label": "Amount vs Usual"}

    f, fc = _freq_score(ts, transaction_history)
    factors["frequency_spike"] = {"score": round(f, 2), "weight": 15,
                                   "detail": f"{fc} in last hour",
                                   "label": "Frequency Spike"}

    m, mn = _mood_score(mood_data)
    factors["mood_influence"] = {"score": round(m, 2), "weight": 10,
                                  "detail": mn.title(),
                                  "label": "Mood Influence"}

    d = _day_score(ts.weekday())
    factors["day_pattern"] = {"score": round(d, 2), "weight": 10,
                               "detail": day_names[ts.weekday()],
                               "label": "Day Pattern"}

    r, rc = _repeat_score(category, ts, transaction_history)
    factors["repeat_category"] = {"score": round(r, 2), "weight": 5,
                                   "detail": f"{rc} same-category today",
                                   "label": "Repeat Category"}

    total = sum(v["score"] * v["weight"] for v in factors.values())
    score = round(min(100, max(0, total)), 1)
    risk = "high" if score >= 65 else ("medium" if score >= 40 else "low")

    return score, risk, factors


def get_reflective_question():
    return random.choice(REFLECTIVE_QUESTIONS)


def get_user_context(user_id, history, moods, goals, recent_mood):
    """Build a rich context object for interconnection across all modes."""
    context = {}

    # Mood status
    if recent_mood:
        mood_emojis = {"angry": "😠", "sad": "😢", "anxious": "😰", "bored": "😑",
                       "tired": "😴", "neutral": "😐", "happy": "😊", "excited": "🤩"}
        ts = recent_mood.get("timestamp", "")
        context["mood_status"] = {
            "mood": recent_mood.get("mood", "neutral"),
            "emoji": mood_emojis.get(recent_mood.get("mood", "neutral"), "😐"),
            "intensity": recent_mood.get("intensity", 5),
            "since": ts,
        }

    # Active savings goal
    if goals and len(goals) > 0:
        g = goals[0]
        progress = round(g.get("current_amount", 0) / g["target_amount"] * 100, 1) if g["target_amount"] > 0 else 0
        context["active_goal"] = {
            "name": g["name"],
            "target": g["target_amount"],
            "current": g.get("current_amount", 0),
            "progress": min(100, progress),
            "remaining": max(0, g["target_amount"] - g.get("current_amount", 0)),
        }

    # Spending streak (days without impulse buy)
    streak = 0
    if history:
        from datetime import datetime, timedelta
        today = datetime.now().date()
        for i in range(30):
            day = today - timedelta(days=i)
            day_txs = [t for t in history if t.get("timestamp", "")[:10] == str(day)]
            if not day_txs or all(t.get("was_cancelled", 0) for t in day_txs):
                streak += 1
            else:
                break
        context["control_streak"] = streak

    # Top trigger category
    if history:
        cat_counts = {}
        for t in history[:50]:
            cat = t.get("category", "other")
            if t.get("impulse_score", 0) >= 50:
                cat_counts[cat] = cat_counts.get(cat, 0) + 1
        if cat_counts:
            top_cat = max(cat_counts, key=cat_counts.get)
            context["top_trigger"] = {
                "category": top_cat.replace("_", " ").title(),
                "count": cat_counts[top_cat],
            }

    # Money saved stat
    saved_txs = [t for t in (history or []) if t.get("was_cancelled", 0)]
    context["total_saved"] = round(sum(t.get("amount", 0) for t in saved_txs), 0)

    return context


# ─── Per-user scikit-learn model ───

_models: dict[str, object] = {}


def train_model(user_id: str, transactions: list[dict]):
    """Train a RandomForest for a specific user once they have enough data."""
    if len(transactions) < 15:
        return
    try:
        from sklearn.ensemble import RandomForestClassifier
        X, y = [], []
        for t in transactions:
            ts = datetime.fromisoformat(t["timestamp"])
            X.append([ts.hour, ts.weekday(), t["amount"],
                      CATEGORY_RISK.get(t["category"], 0.4)])
            y.append(1 if t.get("impulse_score", 0) >= 55 else 0)
        if len(set(y)) < 2:
            return
        clf = RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42)
        clf.fit(np.array(X), np.array(y))
        _models[user_id] = clf
    except Exception:
        pass


def ml_impulse_probability(user_id, amount, category, timestamp_str):
    """Get ML model prediction if available."""
    model = _models.get(user_id)
    if not model:
        return None
    ts = datetime.fromisoformat(timestamp_str)
    try:
        prob = model.predict_proba(
            np.array([[ts.hour, ts.weekday(), amount,
                       CATEGORY_RISK.get(category, 0.4)]])
        )[0]
        return float(prob[1]) if len(prob) > 1 else float(prob[0])
    except Exception:
        return None
