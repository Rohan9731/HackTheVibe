"""Trigger Mapping AI — personal spending pattern analysis per user."""
from datetime import datetime
from collections import defaultdict
import numpy as np


def build_heatmap(transactions: list[dict]) -> list[list[float]]:
    """7 × 24 grid: rows = Mon–Sun, cols = hours."""
    grid = [[0.0] * 24 for _ in range(7)]
    for t in transactions:
        ts = datetime.fromisoformat(t["timestamp"])
        grid[ts.weekday()][ts.hour] += t["amount"]
    return [[round(v, 0) for v in row] for row in grid]


def build_category_by_hour(transactions: list[dict]) -> dict:
    cat_hours: dict[str, list[float]] = defaultdict(lambda: [0.0] * 24)
    for t in transactions:
        ts = datetime.fromisoformat(t["timestamp"])
        cat_hours[t["category"]][ts.hour] += t["amount"]
    return {k: [round(v, 0) for v in lst] for k, lst in cat_hours.items()}


def _peak_slot(grid):
    best = (0, 0, 0.0)
    for d in range(7):
        for h in range(24):
            if grid[d][h] > best[2]:
                best = (d, h, grid[d][h])
    return best


def _top_categories(transactions, n=5):
    totals: dict[str, float] = defaultdict(float)
    for t in transactions:
        totals[t["category"]] += t["amount"]
    return sorted(totals.items(), key=lambda x: x[1], reverse=True)[:n]


def _late_night_cat(transactions):
    totals: dict[str, float] = defaultdict(float)
    for t in transactions:
        h = datetime.fromisoformat(t["timestamp"]).hour
        if h >= 22 or h <= 4:
            totals[t["category"]] += t["amount"]
    return max(totals, key=totals.get) if totals else None


def _weekend_ratio(transactions):
    we, wd = [], []
    for t in transactions:
        d = datetime.fromisoformat(t["timestamp"]).weekday()
        (we if d >= 5 else wd).append(t["amount"])
    avg_we = float(np.mean(we)) if we else 0
    avg_wd = float(np.mean(wd)) if wd else 1
    return round(avg_we / avg_wd, 1) if avg_wd > 0 else 0


def generate_insights(transactions):
    if len(transactions) < 3:
        return ["📊 Make a few more transactions and patterns will start to emerge!"]
    insights = []
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    grid = build_heatmap(transactions)
    pd, ph, pv = _peak_slot(grid)
    if pv > 0:
        insights.append(
            f"🔥 Peak spending: **{days[pd]}s around {ph:02d}:00** (₹{pv:,.0f} total)")
    lnc = _late_night_cat(transactions)
    if lnc:
        insights.append(
            f"🌙 Late-night weakness: **{lnc.replace('_', ' ').title()}** after 10 PM")
    r = _weekend_ratio(transactions)
    if r > 1.3:
        insights.append(f"📅 Weekend spending is **{r}×** your weekday average")
    elif r < 0.7 and r > 0:
        insights.append(f"📅 You actually spend **less** on weekends — good discipline!")
    tc = _top_categories(transactions)
    if tc:
        insights.append(
            f"🏷️ Top category: **{tc[0][0].replace('_', ' ').title()}** (₹{tc[0][1]:,.0f})")
    high = [t for t in transactions if t.get("impulse_score", 0) >= 55]
    if transactions:
        pct = round(len(high) / len(transactions) * 100)
        if pct > 50:
            insights.append(f"⚠️ **{pct}%** of transactions are impulse-risk — let's work on that!")
        elif pct > 20:
            insights.append(f"🔶 **{pct}%** impulse-risk rate — room for improvement")
        else:
            insights.append(f"✅ Only **{pct}%** impulse-risk — you're doing great!")
    cancelled = [t for t in transactions if t.get("was_cancelled")]
    if cancelled:
        saved = sum(t["amount"] for t in cancelled)
        insights.append(f"💰 You've saved **₹{saved:,.0f}** by cancelling impulse purchases!")
    return insights


def get_trigger_data(transactions):
    return {
        "heatmap": build_heatmap(transactions),
        "category_by_hour": build_category_by_hour(transactions),
        "top_categories": _top_categories(transactions),
        "insights": generate_insights(transactions),
        "weekend_ratio": _weekend_ratio(transactions),
        "transaction_count": len(transactions),
    }
