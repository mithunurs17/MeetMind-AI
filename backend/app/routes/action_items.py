"""action_items.py — Action item updates with strict ownership enforcement."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.crud.action_item import get_action_item, update_action_item
from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.action_item import ActionItemResponse, ActionItemUpdate

router = APIRouter()


def _is_admin(user: User) -> bool:
    role = user.role
    if isinstance(role, UserRole):
        return role == UserRole.ADMIN
    return str(role).lower() == "admin"


@router.put(
    "/action-item/{action_item_id}",
    response_model=ActionItemResponse,
    tags=["Action Items"],
    summary="Update an action item (owner or admin only)",
)
def update_action_item_status(
    action_item_id: int,
    payload: ActionItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = get_action_item(db, action_item_id)
    if not item:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Action item not found")

    if not _is_admin(current_user):
        # Verify the action item belongs to a meeting owned by this user
        if item.meeting.owner_id != current_user.id:
            # Return 404 to avoid leaking existence of other users' items
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Action item not found")

    updated = update_action_item(db, action_item_id, payload)
    if not updated:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Could not update action item")
    return updated