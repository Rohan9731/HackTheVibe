"""Mood router — per-user mood check-ins and correlation."""
from fastapi import APIRouter, Request
from datetime import datetime, timezone
from app import database as db
from app.models import MoodCreate
from app.ml.mood_correlator import correlate, get_mood_category_map, MOOD_EMOJIS

router = APIRouter(prefix="/api/mood", tags=["mood"])


def _get_user(request: Request) -> str:
    return request.cookies.get("vibeshield_user", "")


@router.post("/checkin")
async def mood_checkin(mood: MoodCreate, request: Request):
    uid = _get_user(request)
    if not uid:
        return {"error": "Not logged in"}
    ts = datetime.now(timezone.utc).isoformat()
    mid = db.insert_mood(uid, {
        "mood": mood.mood,
        "emoji": mood.emoji or MOOD_EMOJIS.get(mood.mood, "🔵"),
        "intensity": mood.intensity,
        "timestamp": ts,
        "notes": mood.notes,
    })
    return {"status": "logged", "mood_id": mid, "message": "Your mood will influence future impulse detection!"}


@router.get("/correlation")
async def get_correlation(request: Request):
    uid = _get_user(request)
    if not uid:
        return {"error": "Not logged in"}
    txs = db.get_committed_transactions(uid)
    moods = db.get_all_moods(uid)
    result = correlate(txs, moods)
    result["category_map"] = get_mood_category_map(txs, moods)
    result["mood_count_total"] = len(moods)
    result["recent_moods"] = moods[:10]
    return result


@router.get("/recent")
async def get_recent_mood(request: Request):
    uid = _get_user(request)
    if not uid:
        return {"error": "Not logged in"}
    m = db.get_recent_mood(uid)
    return {"mood": m}
