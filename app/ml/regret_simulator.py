"""Future Regret Simulator + AI Conversational Interceptor."""
import random
from datetime import datetime

REGRET_PROB = {
    "food_delivery": 0.55, "gaming": 0.72, "online_shopping": 0.65,
    "entertainment": 0.40, "alcohol": 0.78, "clothing": 0.50,
    "electronics": 0.45, "subscriptions": 0.30, "groceries": 0.05,
    "utilities": 0.02, "transport": 0.05, "healthcare": 0.03,
    "education": 0.05, "rent": 0.01, "other": 0.35,
}


def regret_prediction(amount, category):
    p = REGRET_PROB.get(category, 0.35)
    pct = int(p * 100)
    if p >= 0.6:
        return {
            "probability": pct,
            "level": "high",
            "message": f"⚠️ {pct}% of users with similar patterns regretted this within 3 days.",
        }
    if p >= 0.35:
        return {
            "probability": pct,
            "level": "medium",
            "message": f"🔶 About {pct}% of similar purchases are later considered unnecessary.",
        }
    return {
        "probability": pct,
        "level": "low",
        "message": "✅ This looks like a planned purchase — low regret likelihood.",
    }


def savings_impact(amount, savings_goals):
    if not savings_goals:
        projected = amount * 5
        yearly = amount * 52
        return (
            f"💡 Skipping this 5 times saves **₹{projected:,.0f}**. "
            f"Weekly savings like this = **₹{yearly:,.0f}/year**."
        )
    g = savings_goals[0]
    rem = g["target_amount"] - g.get("current_amount", 0)
    if rem <= 0:
        return "🎉 You've already hit your savings goal! Keep the momentum going."
    if amount <= 0:
        return ""
    skips = max(1, int(rem / amount))
    pct = min(100, round(amount / rem * 100, 1))
    return (
        f"🎯 This ₹{amount:,.0f} is **{pct}%** of what you need for **{g['name']}**. "
        f"Skip it **{skips} times** and you've fully funded your goal!"
    )


def ai_intercept_message(amount, category, impulse_score, savings_goals,
                          recent_mood=None, user_name="User", contacts=None):
    """Generate a personalized AI interceptor message based on all context."""
    cat = category.replace("_", " ")
    msgs = []

    if impulse_score >= 55:
        # High risk messages — personalized
        if savings_goals:
            g = savings_goals[0]
            delay = max(1, int(amount / 150))
            msgs.append(
                f"Hey {user_name}, you're saving for **{g['name']}**. "
                f"This ₹{amount:,.0f} on {cat} delays that goal by ~{delay} days. "
                f"Still want to proceed?"
            )
        if recent_mood and recent_mood.get("mood") in ("sad", "angry", "bored", "tired", "anxious"):
            mood = recent_mood["mood"]
            msgs.append(
                f"You recently felt **{mood}**. Research shows spending when "
                f"{mood} has a **{random.randint(65, 85)}% higher** regret rate. "
                f"Take a breath first?"
            )
        msgs.append(
            f"🌙 Late-night + {cat} = classic impulse combo. "
            f"₹{amount:,.0f} is a lot for something you might not need. Pause and think."
        )
        msgs.append(
            f"{user_name}, your impulse score is {impulse_score:.0f}/100. "
            f"A 20-second pause could save you ₹{amount:,.0f}. Let's breathe."
        )
        if contacts:
            c = contacts[0]
            msgs.append(
                f"📱 Alert: **{c['name']}** would be notified about this "
                f"₹{amount:,.0f} {cat} purchase. Still sure?"
            )
    elif impulse_score >= 40:
        msgs.append(
            f"Quick check — is this ₹{amount:,.0f} on {cat} planned, "
            f"or did something catch your eye? 🤔"
        )
        msgs.append(
            f"This is slightly above your usual pattern. "
            f"Just confirming this {cat} purchase is intentional! 👍"
        )
    else:
        msgs.append(f"✅ Looks planned and responsible. Go ahead, {user_name}!")
        msgs.append(f"This {cat} purchase fits your normal pattern. All good! 👍")

    return random.choice(msgs)
