"""Mood-to-Money Correlation Engine — links emotional states to spending."""
from datetime import datetime, timedelta
from collections import defaultdict


def _mean(lst):
    return sum(lst) / len(lst) if lst else 0

MOOD_EMOJIS = {
    "happy": "😊", "neutral": "😐", "sad": "😔", "angry": "😡",
    "tired": "😴", "bored": "🥱", "anxious": "😰", "excited": "🤩",
}


def correlate(transactions, moods):
    """Correlate moods with spending in ±6 hour windows."""
    if not moods or not transactions:
        return {
            "mood_spend": {}, "mood_count": {}, "baseline_avg": 0,
            "insights": ["Log some moods and make transactions to see how emotions affect your spending!"],
            "mood_timeline": [],
        }

    tx_by_ts = []
    for t in transactions:
        try:
            tx_by_ts.append((datetime.fromisoformat(t["timestamp"]), t["amount"], t["category"]))
        except Exception:
            pass

    mood_totals: dict[str, list[float]] = defaultdict(list)
    timeline = []

    for m in moods:
        try:
            mts = datetime.fromisoformat(m["timestamp"])
        except Exception:
            continue
        ws = mts - timedelta(hours=6)
        we = mts + timedelta(hours=6)
        spend = sum(amt for ts, amt, _ in tx_by_ts if ws <= ts <= we)
        mood_totals[m["mood"]].append(spend)
        timeline.append({
            "date": mts.strftime("%Y-%m-%d %H:%M"),
            "mood": m["mood"],
            "emoji": m.get("emoji", MOOD_EMOJIS.get(m["mood"], "🔵")),
            "spend": round(spend, 0),
            "intensity": m.get("intensity", 5),
        })

    mood_spend = {k: round(_mean(v), 0) for k, v in mood_totals.items()}
    mood_count = {k: len(v) for k, v in mood_totals.items()}
    all_s = [s for lst in mood_totals.values() for s in lst]
    baseline = _mean(all_s)

    insights = []
    if baseline > 0:
        for mood, avg in sorted(mood_spend.items(), key=lambda x: x[1], reverse=True):
            ratio = avg / baseline if baseline > 0 else 0
            emoji = MOOD_EMOJIS.get(mood, "🔵")
            if ratio >= 2.0:
                insights.append(f"{emoji} You spend **{ratio:.1f}× more** when **{mood}** — a major trigger!")
            elif ratio >= 1.3:
                insights.append(f"{emoji} **{mood.title()}** moods increase spending by **{int((ratio - 1) * 100)}%**")
            elif ratio <= 0.5 and ratio > 0:
                insights.append(f"{emoji} When **{mood}**, you spend **{int((1 - ratio) * 100)}% less** — nice control!")

    if not insights:
        insights.append("Keep logging moods — spending patterns will emerge soon!")

    return {
        "mood_spend": mood_spend,
        "mood_count": mood_count,
        "baseline_avg": round(baseline, 0),
        "insights": insights,
        "mood_timeline": sorted(timeline, key=lambda x: x["date"]),
    }


def get_mood_category_map(transactions, moods):
    """Which categories do users spend on when in each mood?"""
    if not moods or not transactions:
        return {}
    tx = []
    for t in transactions:
        try:
            tx.append((datetime.fromisoformat(t["timestamp"]), t["amount"], t["category"]))
        except Exception:
            pass
    result: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for m in moods:
        try:
            mts = datetime.fromisoformat(m["timestamp"])
        except Exception:
            continue
        ws = mts - timedelta(hours=6)
        we = mts + timedelta(hours=6)
        for ts, amt, cat in tx:
            if ws <= ts <= we:
                result[m["mood"]][cat] += amt
    return {mood: {c: round(v, 0) for c, v in cats.items()} for mood, cats in result.items()}
