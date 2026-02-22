"""Pydantic models for VibeShield API."""
from pydantic import BaseModel
from typing import Optional


class TransactionCreate(BaseModel):
    amount: float
    merchant: str
    category: str
    timestamp: Optional[str] = None   # ISO string, auto-filled if None


class TransactionOutcome(BaseModel):
    transaction_id: int
    was_paused: bool = False
    was_overridden: bool = False
    was_cancelled: bool = False
    pause_duration: float = 0


class MoodCreate(BaseModel):
    mood: str
    emoji: str
    intensity: int = 5
    notes: str = ""


class SavingsGoalCreate(BaseModel):
    name: str
    target_amount: float
    deadline: str = ""


class AccountabilityContactCreate(BaseModel):
    name: str
    phone: str = ""
    email: str = ""


class UserSettingsUpdate(BaseModel):
    lock_duration: int = 20
    lock_sensitivity: str = "medium"
    enable_accountability: bool = True
    enable_breathing: bool = True
    enable_mood_alerts: bool = True
