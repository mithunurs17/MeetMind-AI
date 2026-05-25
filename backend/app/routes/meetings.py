from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud.meeting import get_meeting, get_all_meetings, delete_meeting
from app.schemas.meeting import MeetingResponse

router = APIRouter()


@router.get("/meetings", response_model=list[MeetingResponse], tags=["Meetings"])
def read_meetings(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """Retrieve a list of meetings."""
    return get_all_meetings(db, skip=skip, limit=limit)


@router.get("/meeting/{meeting_id}", response_model=MeetingResponse, tags=["Meetings"])
def read_meeting(meeting_id: int, db: Session = Depends(get_db)):
    """Retrieve a single meeting by ID."""
    meeting = get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found"
        )
    return meeting


@router.delete("/meeting/{meeting_id}", tags=["Meetings"], status_code=status.HTTP_200_OK)
def remove_meeting(meeting_id: int, db: Session = Depends(get_db)):
    """Delete a meeting by ID."""
    meeting = delete_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found"
        )
    return {"detail": "Meeting deleted successfully"}
