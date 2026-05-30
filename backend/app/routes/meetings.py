"""
meetings.py — Meeting CRUD, now owner-scoped.

- Regular users   : see / delete only their own meetings
- Admin users     : see / delete ALL meetings
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload

from app.core.dependencies import get_current_user, require_admin
from app.crud.meeting import delete_meeting, get_all_meetings, get_meeting
from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.meeting import MeetingResponse

router = APIRouter()


def _user_meetings(db: Session, user: User, skip: int, limit: int):
    """Return meetings scoped to the user's role."""
    from app.models.meeting import Meeting

    q = db.query(Meeting).options(
        selectinload(Meeting.action_items),
        selectinload(Meeting.decisions),
        selectinload(Meeting.risks),
    )
    if user.role != UserRole.ADMIN:
        q = q.filter(Meeting.owner_id == user.id)
    return q.order_by(Meeting.created_at.desc()).offset(skip).limit(limit).all()


@router.get(
    "/meetings",
    response_model=list[MeetingResponse],
    tags=["Meetings"],
    summary="List meetings (scoped to the authenticated user)",
)
def read_meetings(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _user_meetings(db, current_user, skip, limit)


@router.get(
    "/meeting/{meeting_id}",
    response_model=MeetingResponse,
    tags=["Meetings"],
)
def read_meeting(
    meeting_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    meeting = get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Meeting not found")
    if current_user.role != UserRole.ADMIN and meeting.owner_id != current_user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not authorised to view this meeting")
    return meeting


@router.delete(
    "/meeting/{meeting_id}",
    tags=["Meetings"],
    status_code=status.HTTP_200_OK,
)
def remove_meeting(
    meeting_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    meeting = get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Meeting not found")
    if current_user.role != UserRole.ADMIN and meeting.owner_id != current_user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not authorised to delete this meeting")
    delete_meeting(db, meeting_id)
    return {"detail": "Meeting deleted successfully"}