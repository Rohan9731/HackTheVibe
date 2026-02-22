"""
Seed demo data — generates realistic 30-day transaction & mood history for a user.
Called on-demand via API, NOT automatically.
"""
import random
from datetime import datetime, timedelta, timezone
from app import database as db
from app.ml.impulse_engine import calculate_impulse_score, CATEGORY_RISK

MERCHANTS = {
    "food_delivery": ["Swiggy", "Zomato", "Uber Eats", "Domino's"],
    "gaming": ["Steam", "PlayStation Store", "Google Play Games", "Epic Games"],
    "online_shopping": ["Amazon", "Flipkart", "Myntra", "Meesho"],
    "entertainment": ["Netflix", "BookMyShow", "Spotify", "Disney+"],
    "alcohol": ["Drizly", "Wine Shop", "Liquor Store"],
    "clothing": ["Zara", "H&M", "Uniqlo", "Nike"],
    "electronics": ["Croma", "Apple Store", "Samsung", "Reliance Digital"],
    "groceries": ["BigBasket", "Blinkit", "DMart", "Zepto"],
    "utilities": ["Electricity Board", "Jio", "Airtel", "Water Bill"],
    "transport": ["Uber", "Ola", "Metro Card", "Rapido"],
    "healthcare": ["Apollo Pharmacy", "1mg", "Practo"],
    "education": ["Udemy", "Coursera", "Amazon Books"],
    "subscriptions": ["YouTube Premium", "iCloud", "ChatGPT Plus"],
}

MOOD_LIST = [
    ("happy", "😊"), ("neutral", "😐"), ("sad", "😔"), ("angry", "😡"),
    ("tired", "😴"), ("bored", "🥱"), ("anxious", "😰"), ("excited", "🤩"),
]


def seed_user_data(user_id: str, days: int = 30, tx_per_day: tuple = (2, 6)):
    """Generate realistic demo data for a user."""
    now = datetime.now(timezone.utc)

    # Generate moods first (1-3 per day)
    moods_generated = []
    for d in range(days):
        day = now - timedelta(days=days - d)
        n_moods = random.randint(1, 2)
        for _ in range(n_moods):
            hour = random.choice([8, 12, 15, 19, 22, 1])
            ts = day.replace(hour=hour, minute=random.randint(0, 59))
            mood, emoji = random.choice(MOOD_LIST)
            # Weight negative moods on weekends and late hours
            if ts.weekday() >= 5 or hour >= 22:
                mood, emoji = random.choices(
                    MOOD_LIST, weights=[1, 2, 3, 2, 3, 4, 3, 1], k=1
                )[0]
            intensity = random.randint(3, 9)
            db.insert_mood(user_id, {
                "mood": mood, "emoji": emoji,
                "intensity": intensity, "timestamp": ts.isoformat(),
            })
            moods_generated.append({"mood": mood, "emoji": emoji,
                                     "intensity": intensity, "timestamp": ts.isoformat()})

    # Generate transactions
    tx_count = 0
    for d in range(days):
        day = now - timedelta(days=days - d)
        n = random.randint(*tx_per_day)

        for _ in range(n):
            # Heavier spending late night and weekends
            if random.random() < 0.35:
                hour = random.choice([22, 23, 0, 1, 2, 3])
            else:
                hour = random.choice(list(range(8, 22)))

            minute = random.randint(0, 59)
            ts = day.replace(hour=hour, minute=minute)

            # Pick category with bias toward impulse categories
            cats = list(MERCHANTS.keys())
            weights = [CATEGORY_RISK.get(c, 0.3) + 0.1 for c in cats]
            category = random.choices(cats, weights=weights, k=1)[0]
            merchant = random.choice(MERCHANTS[category])

            # Amount based on category
            base_amounts = {
                "food_delivery": (150, 900), "gaming": (200, 4000),
                "online_shopping": (300, 8000), "entertainment": (100, 2000),
                "alcohol": (300, 3000), "clothing": (500, 5000),
                "electronics": (1000, 15000), "groceries": (200, 1500),
                "utilities": (200, 2000), "transport": (50, 500),
                "healthcare": (100, 3000), "education": (200, 5000),
                "subscriptions": (99, 999),
            }
            lo, hi = base_amounts.get(category, (100, 2000))
            amount = round(random.uniform(lo, hi), 0)

            # Get moods up to this point for scoring
            past_moods = [m for m in moods_generated
                          if m["timestamp"] <= ts.isoformat()][-5:]

            history = db.get_committed_transactions(user_id, limit=100)
            score, risk, _ = calculate_impulse_score(
                amount, category, ts.isoformat(), history, past_moods
            )

            # Simulate some being cancelled (30% of high-risk)
            was_cancelled = 0
            if score >= 55 and random.random() < 0.3:
                was_cancelled = 1

            db.insert_transaction(user_id, {
                "amount": amount, "merchant": merchant,
                "category": category, "timestamp": ts.isoformat(),
                "impulse_score": score, "risk_level": risk,
                "was_paused": 1 if score >= 48 else 0,
                "was_overridden": 1 if score >= 48 and not was_cancelled else 0,
                "was_cancelled": was_cancelled,
            })
            tx_count += 1

    # Add a savings goal
    db.insert_savings_goal(user_id, {
        "name": "New MacBook Pro",
        "target_amount": 150000,
        "current_amount": random.randint(5000, 25000),
        "deadline": (now + timedelta(days=180)).strftime("%Y-%m-%d"),
        "created_at": (now - timedelta(days=days)).isoformat(),
    })

    # Add accountability contact
    db.insert_accountability_contact(user_id, {
        "name": "Priya (Best Friend)",
        "phone": "+91 98765 43210",
        "email": "priya@example.com",
    })

    return {"transactions": tx_count, "moods": len(moods_generated),
            "goals": 1, "contacts": 1}
