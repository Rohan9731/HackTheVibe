"""Dashboard router — per-user analytics, charts, gamification."""
from fastapi import APIRouter, Request
from datetime import datetime, timezone
from app import database as db
from app.models import SavingsGoalCreate, AccountabilityContactCreate
from app.ml.trigger_mapper import get_trigger_data
from app.ml.mood_correlator import correlate
import numpy as np

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


def _get_user(request: Request) -> tuple[str, str]:
    uid = request.cookies.get("vibeshield_user", "")
    name = request.cookies.get("vibeshield_name", "User")
    return uid, name


@router.get("/stats")
async def get_stats(request: Request):
    uid, uname = _get_user(request)
    if not uid:
        return {"error": "Not logged in"}

    stats = db.get_user_stats(uid)
    txs = db.get_committed_transactions(uid)
    all_tx = db.get_all_transactions(uid)
    goals = db.get_savings_goals(uid)
    contacts = db.get_accountability_contacts(uid)

    # Calculate streaks and scores
    scores = [t.get("impulse_score", 0) for t in txs]
    avg_score = round(float(np.mean(scores)), 1) if scores else 0
    total_spent = round(sum(t["amount"] for t in txs), 0)

    # Category breakdown for charts
    cat_totals: dict[str, float] = {}
    for t in txs:
        cat_totals[t["category"]] = cat_totals.get(t["category"], 0) + t["amount"]

    # Daily spending for chart (last 30 days)
    daily: dict[str, float] = {}
    for t in txs:
        day = t["timestamp"][:10]
        daily[day] = daily.get(day, 0) + t["amount"]

    # Self-control streak (consecutive low-risk)
    streak = 0
    for t in all_tx:
        if t.get("was_cancelled"):
            streak += 1
        elif t.get("impulse_score", 0) < 40:
            streak += 1
        else:
            break

    # Gamification level
    saves = stats["cancelled_count"]
    if saves >= 20:
        level = {"name": "Zen Master", "emoji": "🧘", "tier": 5}
    elif saves >= 10:
        level = {"name": "Impulse Warrior", "emoji": "⚔️", "tier": 4}
    elif saves >= 5:
        level = {"name": "Smart Saver", "emoji": "💎", "tier": 3}
    elif saves >= 2:
        level = {"name": "Mindful Spender", "emoji": "🌱", "tier": 2}
    elif saves >= 1:
        level = {"name": "Awareness Beginner", "emoji": "🌟", "tier": 1}
    else:
        level = {"name": "Just Starting", "emoji": "🚀", "tier": 0}

    return {
        "user_name": uname,
        "total_transactions": stats["total_transactions"],
        "total_spent": total_spent,
        "money_saved": stats["money_saved"],
        "cancelled_count": stats["cancelled_count"],
        "avg_impulse_score": avg_score,
        "mood_entries": stats["mood_entries"],
        "self_control_streak": streak,
        "level": level,
        "category_breakdown": cat_totals,
        "daily_spending": daily,
        "savings_goals": goals,
        "contacts": contacts,
        "recent_transactions": all_tx[:10],
    }


@router.get("/triggers")
async def get_triggers(request: Request):
    uid, _ = _get_user(request)
    if not uid:
        return {"error": "Not logged in"}
    txs = db.get_all_transactions(uid)
    return get_trigger_data(txs)


@router.get("/mood-correlation")
async def get_mood_corr(request: Request):
    uid, _ = _get_user(request)
    if not uid:
        return {"error": "Not logged in"}
    txs = db.get_committed_transactions(uid)
    moods = db.get_all_moods(uid)
    return correlate(txs, moods)


@router.post("/savings-goal")
async def add_savings_goal(goal: SavingsGoalCreate, request: Request):
    uid, _ = _get_user(request)
    if not uid:
        return {"error": "Not logged in"}
    gid = db.insert_savings_goal(uid, {
        "name": goal.name,
        "target_amount": goal.target_amount,
        "deadline": goal.deadline,
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    return {"status": "created", "goal_id": gid}


@router.post("/accountability-contact")
async def add_contact(contact: AccountabilityContactCreate, request: Request):
    uid, _ = _get_user(request)
    if not uid:
        return {"error": "Not logged in"}
    cid = db.insert_accountability_contact(uid, {
        "name": contact.name,
        "phone": contact.phone,
        "email": contact.email,
    })
    return {"status": "added", "contact_id": cid}


@router.post("/clear-data")
async def clear_data(request: Request):
    uid, _ = _get_user(request)
    if not uid:
        return {"error": "Not logged in"}
    db.clear_user_data(uid)
    return {"status": "cleared"}
