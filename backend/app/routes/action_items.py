from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.action_item import ActionItemUpdate, ActionItemResponse
from app.crud.action_item import update_action_item, get_action_item

router = APIRouter()


@router.put("/action-item/{action_item_id}", response_model=ActionItemResponse, tags=["Action Items"])
def update_action_item_status(action_item_id: int, payload: ActionItemUpdate, db: Session = Depends(get_db)):
    """Update the details of a specific action item."""
    existing = get_action_item(db, action_item_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action item not found"
        )

    updated = update_action_item(db, action_item_id, payload)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not update action item"
        )
    return updated
