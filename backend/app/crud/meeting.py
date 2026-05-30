from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session, selectinload

from app.models.action_item import ActionItem
from app.models.decision import Decision
from app.models.meeting import Meeting
from app.models.risk import Risk
from app.schemas.meeting import MeetingCreate


def get_meeting(db: Session, meeting_id: int) -> Optional[Meeting]:
    return (
        db.query(Meeting)
        .options(
            selectinload(Meeting.action_items),
            selectinload(Meeting.decisions),
            selectinload(Meeting.risks),
        )
        .filter(Meeting.id == meeting_id)
        .first()
    )


def get_all_meetings(db: Session, skip: int = 0, limit: int = 20) -> list[Meeting]:
    return (
        db.query(Meeting)
        .order_by(Meeting.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
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
    meeting = Meeting(
        title=generated.get("title") or "AI Generated Meeting",
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