from sqlalchemy.orm import Session
from app.models.action_item import ActionItem
from app.schemas.action_item import ActionItemUpdate


def get_action_item(db: Session, action_item_id: int):
    return db.query(ActionItem).filter(ActionItem.id == action_item_id).first()


def update_action_item(db: Session, action_item_id: int, update_data: ActionItemUpdate):
    action_item = get_action_item(db, action_item_id)
    if not action_item:
        return None

    values = update_data.model_dump(exclude_unset=True)
    for key, value in values.items():
        setattr(action_item, key, value)
    db.add(action_item)
    db.commit()
    db.refresh(action_item)
    return action_item
