"""
trial.py — One free extraction per IP address, no account required.

The trial usage is tracked in the `trial_uses` table (IP + used_at).
Once an IP has one record, further anonymous calls are rejected with 403
and a prompt to register/login.
"""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import Session

from app.database import Base, get_db
from app.schemas.meeting import MeetingAIRequest, MeetingResponse
from app.services.ai_service import extract_structured_meeting
from app.crud.meeting import save_ai_generated

router = APIRouter()


# ── Tiny model — lives in same DB, no migration needed (create_all handles it)
class TrialUse(Base):
    __tablename__ = "trial_uses"
    id         = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String(64), nullable=False, unique=True, index=True)
    used_at    = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


def _client_ip(request: Request) -> str:
    xff = request.headers.get("X-Forwarded-For")
    if xff:
        return xff.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def has_used_trial(db: Session, ip: str) -> bool:
    return db.query(TrialUse).filter(TrialUse.ip_address == ip).first() is not None


def record_trial_use(db: Session, ip: str) -> None:
    db.add(TrialUse(ip_address=ip))
    db.commit()


# ── Route ─────────────────────────────────────────────────────────────────
@router.post(
    "/trial/extract",
    response_model=MeetingResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Trial"],
    summary="One free AI extraction — no account needed (once per IP)",
)
def trial_extract(
    transcript: MeetingAIRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    ip = _client_ip(request)

    if has_used_trial(db, ip):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Free trial already used for this network address. "
                "Please create a free account to continue."
            ),
        )

    if not transcript.raw_text or not transcript.raw_text.strip():
        raise HTTPException(status_code=400, detail="raw_text is required")

    try:
        structured = extract_structured_meeting(transcript.raw_text, title=transcript.title)
        # Save without an owner — orphan meeting
        saved = save_ai_generated(db, structured, owner_id=None)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    # Only mark as used AFTER a successful extraction
    record_trial_use(db, ip)
    return saved


@router.get(
    "/trial/status",
    tags=["Trial"],
    summary="Check whether the caller's IP has already used its free trial",
)
def trial_status(request: Request, db: Session = Depends(get_db)):
    ip = _client_ip(request)
    used = has_used_trial(db, ip)
    return {"trial_used": used, "ip": ip}