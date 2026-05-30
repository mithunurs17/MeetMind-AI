"""crud/meeting.py — Meeting database operations.

ALL user-facing queries go through get_meetings_for_user() which enforces
owner_id scoping at the SQL level.  Admin queries use get_all_meetings().
"""
from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session, selectinload

from app.models.action_item import ActionItem
from app.models.decision import Decision
from app.models.meeting import Meeting
from app.models.risk import Risk
from app.schemas.meeting import MeetingCreate

# Shared eager-load options
_LOAD_OPTS = [
    selectinload(Meeting.action_items),
    selectinload(Meeting.decisions),
    selectinload(Meeting.risks),
]


def get_meeting(db: Session, meeting_id: int) -> Optional[Meeting]:
    return (
        db.query(Meeting)
        .options(*_LOAD_OPTS)
        .filter(Meeting.id == meeting_id)
        .first()
    )


def get_meetings_for_user(
    db: Session,
    owner_id: int,
    skip: int = 0,
    limit: int = 100,
) -> list[Meeting]:
    """Return ONLY meetings owned by owner_id. Never returns NULL-owner rows."""
    return (
        db.query(Meeting)
        .options(*_LOAD_OPTS)
        .filter(Meeting.owner_id == owner_id)
        .order_by(Meeting.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_all_meetings(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[Meeting]:
    """Return all meetings across all users. Admin use only."""
    return (
        db.query(Meeting)
        .options(*_LOAD_OPTS)
        .order_by(Meeting.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_meeting_for_user(
    db: Session,
    meeting_id: int,
    owner_id: int,
) -> Optional[Meeting]:
    """Return a single meeting only if it is owned by owner_id."""
    return (
        db.query(Meeting)
        .options(*_LOAD_OPTS)
        .filter(Meeting.id == meeting_id, Meeting.owner_id == owner_id)
        .first()
    )


def create_meeting(
    db: Session,
    meeting_data: MeetingCreate,
    owner_id: Optional[int] = None,
) -> Meeting:
    summary = meeting_data.summary
    if not summary:
        summary = meeting_data.raw_text[:600] + (
            "..." if len(meeting_data.raw_text) > 600 else ""
        )

    meeting = Meeting(
        title=meeting_data.title,
        raw_text=meeting_data.raw_text,
        summary=summary,
        owner_id=owner_id,
    )
    db.add(meeting)
    db.flush()

    for item in meeting_data.action_items or []:
        db.add(ActionItem(
            meeting_id=meeting.id,
            task=item.task,
            owner=item.owner,
            due_date=item.due_date,
            status=item.status or "pending",
        ))

    for decision in meeting_data.decisions or []:
        db.add(Decision(meeting_id=meeting.id, decision_text=decision.decision_text))

    for risk in meeting_data.risks or []:
        db.add(Risk(meeting_id=meeting.id, risk_text=risk.risk_text))

    db.commit()
    db.refresh(meeting)
    return get_meeting(db, meeting.id)


def delete_meeting(db: Session, meeting_id: int) -> Optional[Meeting]:
    meeting = get_meeting(db, meeting_id)
    if meeting:
        db.delete(meeting)
        db.commit()
    return meeting


def save_ai_generated(
    db: Session,
    generated: dict,
    owner_id: Optional[int] = None,
) -> Meeting:
    title = (generated.get("title") or "").strip() or "Untitled Meeting"

    meeting = Meeting(
        title=title,
        raw_text=generated.get("raw_text") or "",
        summary=generated.get("summary"),
        owner_id=owner_id,
    )
    db.add(meeting)
    db.flush()

    for ai in generated.get("action_items", []) or []:
        due = None
        if ai.get("due_date"):
            try:
                from dateutil import parser as _p
                due = _p.parse(ai.get("due_date"))
            except Exception:
                due = None
        db.add(ActionItem(
            meeting_id=meeting.id,
            task=ai.get("task") or "",
            owner=ai.get("owner"),
            due_date=due,
            status=ai.get("status") or "pending",
        ))

    for d in generated.get("decisions", []) or []:
        db.add(Decision(meeting_id=meeting.id, decision_text=d))

    for r in generated.get("risks", []) or []:
        db.add(Risk(meeting_id=meeting.id, risk_text=r))

    for q in generated.get("open_questions", []) or []:
        db.add(Risk(meeting_id=meeting.id, risk_text=f"OPEN QUESTION: {q}"))

    db.commit()
    db.refresh(meeting)
    return get_meeting(db, meeting.id)