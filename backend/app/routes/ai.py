"""ai.py — AI extraction routes.

ExtractionError from ai_service maps to HTTP 422 Unprocessable Entity
so the frontend can display a user-friendly message without saving
any broken records to the database.
"""
from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.crud.meeting import save_ai_generated
from app.database import get_db
from app.models.user import User
from app.schemas.meeting import MeetingAIRequest, MeetingResponse
from app.services.ai_service import ExtractionError, extract_structured_meeting

router = APIRouter()


@router.post(
    "/ai/extract",
    response_model=MeetingResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["AI"],
    summary="Extract meeting minutes from pasted text",
)
def ai_extract(
    transcript: MeetingAIRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not transcript.raw_text or not transcript.raw_text.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The transcript is empty. Please paste your meeting notes before submitting.",
        )
    try:
        structured = extract_structured_meeting(
            transcript.raw_text,
            title=transcript.title,
        )
        # Only reaches here if extraction passed validation
        saved = save_ai_generated(db, structured, owner_id=current_user.id)
        return saved
    except ExtractionError as exc:
        # Validation failed — nothing was saved to DB
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during extraction: {exc}",
        )


@router.post(
    "/ai/extract-file",
    response_model=MeetingResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["AI"],
    summary="Extract meeting minutes from an uploaded file",
)
def ai_extract_file(
    file: UploadFile = File(...),
    title: str = Form(default=""),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        from app.utils.ingest import extract_text_from_file
        raw_text = extract_text_from_file(file)

        if not raw_text or not raw_text.strip():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    "No text could be extracted from the uploaded file. "
                    "Please check that the file is not empty and is a supported format (TXT, PDF, DOCX)."
                ),
            )

        meeting_title = title.strip() if title and title.strip() else None
        structured = extract_structured_meeting(raw_text, title=meeting_title)
        saved = save_ai_generated(db, structured, owner_id=current_user.id)
        return saved

    except ExtractionError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during file extraction: {exc}",
        )