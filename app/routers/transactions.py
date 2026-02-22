"""Transaction router — per-user analysis, commit, and outcome recording."""
from fastapi import APIRouter, Request
from datetime import datetime, timezone
from app import database as db
from app.models import TransactionCreate, TransactionOutcome, UserSettingsUpdate
from app.ml.impulse_engine import (
    calculate_impulse_score, get_lock_threshold,
    get_reflective_question, get_reflective_questions,
    ml_impulse_probability, train_model,
    detect_category_from_item, get_user_context, ITEM_TO_CATEGORY
)
from app.ml.regret_simulator import (
    regret_prediction, savings_impact, ai_intercept_message
)

router = APIRouter(prefix="/api/transactions", tags=["transactions"])


def _get_user(request: Request) -> tuple[str, str]:
    uid = request.cookies.get("vibeshield_user", "")
    name = request.cookies.get("vibeshield_name", "User")
    return uid, name


@router.post("/analyze")
async def analyze_transaction(tx: TransactionCreate, request: Request):
    """Analyze a transaction's impulse risk WITHOUT committing it yet."""
    uid, uname = _get_user(request)
    if not uid:
        return {"error": "Not logged in"}

    ts = tx.timestamp or datetime.now(timezone.utc).isoformat()
    history = db.get_committed_transactions(uid, limit=200)
    all_history = db.get_all_transactions(uid, limit=200)
    moods = db.get_all_moods(uid, limit=20)
    goals = db.get_savings_goals(uid)
    contacts = db.get_accountability_contacts(uid)
    recent_mood = db.get_recent_mood(uid)
    tx_count = db.get_transaction_count(uid)
    settings = db.get_user_settings(uid)

    # Apply sensitivity setting to threshold
    score, risk, factors = calculate_impulse_score(
        tx.amount, tx.category, ts, history, moods
    )
    base_threshold = get_lock_threshold(tx_count)
    sensitivity_offset = {"low": 8, "medium": 0, "high": -8}
    threshold = base_threshold + sensitivity_offset.get(settings.get("lock_sensitivity", "medium"), 0)
    should_lock = score >= threshold

    # ML model boost if available
    ml_prob = ml_impulse_probability(uid, tx.amount, tx.category, ts)

    # Regret prediction
    regret = regret_prediction(tx.amount, tx.category)

    # Savings impact
    savings_msg = savings_impact(tx.amount, goals)

    # AI interceptor message
    ai_msg = ai_intercept_message(
        tx.amount, tx.category, score, goals,
        recent_mood=recent_mood, user_name=uname, contacts=contacts
    )

    # Multi-step reflective questions (contextual)
    questions = get_reflective_questions(
        score, tx.category, tx.amount,
        mood_data=moods, goals=goals, history=all_history,
        timestamp_str=ts
    )

    # User context for interconnection
    user_context = get_user_context(uid, all_history, moods, goals, recent_mood)

    # Lock duration from user settings
    lock_duration = settings.get("lock_duration", 20)

    # Accountability alert
    accountability_alert = None
    if contacts and score >= threshold and settings.get("enable_accountability", 1):
        c = contacts[0]
        accountability_alert = (
            f"📱 {c['name']} would be notified: "
            f"\"{uname} is about to spend ₹{tx.amount:,.0f} on "
            f"{tx.category.replace('_', ' ')} (risk: {score:.0f}/100)\""
        )

    return {
        "impulse_score": score,
        "risk_level": risk,
        "factors": factors,
        "should_lock": should_lock,
        "lock_threshold": threshold,
        "lock_duration": lock_duration,
        "ml_probability": ml_prob,
        "regret": regret,
        "savings_impact": savings_msg,
        "ai_message": ai_msg,
        "reflective_question": questions[0]["text"] if questions else "",
        "reflective_questions": questions,
        "accountability_alert": accountability_alert,
        "user_context": user_context,
        "settings": {
            "enable_breathing": bool(settings.get("enable_breathing", 1)),
            "enable_mood_alerts": bool(settings.get("enable_mood_alerts", 1)),
        },
        "transaction_data": {
            "amount": tx.amount,
            "merchant": tx.merchant,
            "category": tx.category,
            "timestamp": ts,
        },
    }


@router.post("/commit")
async def commit_transaction(tx: TransactionCreate, request: Request):
    """Actually save the transaction (user chose to proceed)."""
    uid, _ = _get_user(request)
    if not uid:
        return {"error": "Not logged in"}

    ts = tx.timestamp or datetime.now(timezone.utc).isoformat()
    history = db.get_committed_transactions(uid, limit=200)
    moods = db.get_all_moods(uid, limit=20)

    score, risk, _ = calculate_impulse_score(
        tx.amount, tx.category, ts, history, moods
    )

    tx_id = db.insert_transaction(uid, {
        "amount": tx.amount,
        "merchant": tx.merchant,
        "category": tx.category,
        "timestamp": ts,
        "impulse_score": score,
        "risk_level": risk,
        "was_paused": 0,
        "was_overridden": 0,
        "was_cancelled": 0,
    })

    # Retrain ML model if enough data
    all_tx = db.get_all_transactions(uid)
    train_model(uid, all_tx)

    return {"status": "committed", "transaction_id": tx_id, "impulse_score": score}


@router.post("/cancel")
async def cancel_transaction(tx: TransactionCreate, request: Request):
    """Record a cancelled transaction (user chose NOT to buy)."""
    uid, _ = _get_user(request)
    if not uid:
        return {"error": "Not logged in"}

    ts = tx.timestamp or datetime.now(timezone.utc).isoformat()
    history = db.get_committed_transactions(uid, limit=200)
    moods = db.get_all_moods(uid, limit=20)

    score, risk, _ = calculate_impulse_score(
        tx.amount, tx.category, ts, history, moods
    )

    tx_id = db.insert_transaction(uid, {
        "amount": tx.amount,
        "merchant": tx.merchant,
        "category": tx.category,
        "timestamp": ts,
        "impulse_score": score,
        "risk_level": risk,
        "was_paused": 1,
        "was_overridden": 0,
        "was_cancelled": 1,
    })

    # Credit savings goal if available
    goals = db.get_savings_goals(uid)
    if goals:
        db.update_savings_goal_amount(goals[0]["id"], tx.amount)

    return {
        "status": "cancelled",
        "transaction_id": tx_id,
        "money_saved": tx.amount,
        "impulse_score": score,
        "goal_credited": goals[0]["name"] if goals else None,
    }


@router.post("/outcome")
async def record_outcome(outcome: TransactionOutcome, request: Request):
    """Update a transaction with its final outcome."""
    uid, _ = _get_user(request)
    if not uid:
        return {"error": "Not logged in"}
    db.update_transaction_outcome(
        outcome.transaction_id, outcome.was_paused,
        outcome.was_overridden, outcome.was_cancelled, outcome.pause_duration
    )
    return {"status": "updated"}


@router.get("/recent")
async def get_recent(request: Request):
    """Get recent transactions for the current user."""
    uid, _ = _get_user(request)
    if not uid:
        return {"error": "Not logged in"}
    txs = db.get_all_transactions(uid, limit=20)
    return {"transactions": txs}


@router.get("/settings")
async def get_settings(request: Request):
    """Get user settings."""
    uid, _ = _get_user(request)
    if not uid:
        return {"error": "Not logged in"}
    settings = db.get_user_settings(uid)
    return settings


@router.post("/settings")
async def save_settings(settings: UserSettingsUpdate, request: Request):
    """Save user settings."""
    uid, _ = _get_user(request)
    if not uid:
        return {"error": "Not logged in"}
    db.update_user_settings(uid, settings.dict())
    return {"status": "saved"}


@router.post("/detect-category")
async def detect_category(request: Request):
    """Detect category from item text."""
    uid, _ = _get_user(request)
    if not uid:
        return {"error": "Not logged in"}
    data = await request.json()
    item_text = data.get("item", "").strip()
    if not item_text:
        return {"category": None}
    category = detect_category_from_item(item_text)
    return {"category": category, "item": item_text}


@router.get("/context")
async def get_context(request: Request):
    """Get user context for interconnection across all views."""
    uid, _ = _get_user(request)
    if not uid:
        return {"error": "Not logged in"}
    history = db.get_all_transactions(uid, limit=200)
    moods = db.get_all_moods(uid, limit=20)
    goals = db.get_savings_goals(uid)
    recent_mood = db.get_recent_mood(uid)
    context = get_user_context(uid, history, moods, goals, recent_mood)
    return context
