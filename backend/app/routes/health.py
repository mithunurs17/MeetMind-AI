from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter()


@router.get("/health", tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint to verify API and database connectivity."""
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "service": "MeetMind AI Backend",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "MeetMind AI Backend",
            "database": "disconnected",
            "error": str(e)
        }
