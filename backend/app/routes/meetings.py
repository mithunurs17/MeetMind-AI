"""meetings.py — Meeting CRUD routes with strict per-user data isolation.

Data isolation rules (enforced at both route AND crud level):
  - Regular users : see / modify / delete ONLY their own meetings
  - Admin users   : see / modify / delete ALL meetings
  
The owner_id filter is applied at the SQL level inside the CRUD functions,
NOT just in Python, so it is impossible for a SQL query to return another
user's rows to a non-admin caller.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.crud.meeting import (
    delete_meeting,
    get_all_meetings,
    get_meeting,
    get_meeting_for_user,
    get_meetings_for_user,
)
from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.meeting import MeetingResponse

router = APIRouter()


def _is_admin(user: User) -> bool:
    """Safe admin check that works whether role is an enum or a plain string."""
    role = user.role
    # Handle both enum value and raw string (e.g. after certain ORM loads)
    if isinstance(role, UserRole):
        return role == UserRole.ADMIN
    return str(role).lower() == "admin"


@router.get(
    "/meetings",
    response_model=list[MeetingResponse],
    tags=["Meetings"],
    summary="List meetings for the authenticated user (admins see all)",
)
def read_meetings(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if _is_admin(current_user):
        return get_all_meetings(db, skip=skip, limit=limit)
    # Non-admin: strictly scoped to their own owner_id at the SQL level
    return get_meetings_for_user(db, owner_id=current_user.id, skip=skip, limit=limit)


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
    if _is_admin(current_user):
        meeting = get_meeting(db, meeting_id)
    else:
        # Use the owner-scoped query — returns None if owner_id doesn't match
        meeting = get_meeting_for_user(db, meeting_id, owner_id=current_user.id)

    if not meeting:
        # Return 404 for both "not found" and "not yours" — don't leak existence
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Meeting not found")
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
    if _is_admin(current_user):
        meeting = get_meeting(db, meeting_id)
    else:
        meeting = get_meeting_for_user(db, meeting_id, owner_id=current_user.id)

    if not meeting:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Meeting not found")

    delete_meeting(db, meeting_id)
    return {"detail": "Meeting deleted successfully"}