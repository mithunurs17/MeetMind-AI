from app.crud.meeting import create_meeting, get_meeting, delete_meeting
from app.schemas.meeting import MeetingCreate


def test_create_and_get_meeting(db_session):
    payload = MeetingCreate(
        title="Test Meeting",
        raw_text="This meeting discussed the launch timeline.",
        summary="Meeting summary for unit test."
    )
    meeting = create_meeting(db_session, payload)

    assert meeting.id is not None
    assert meeting.title == "Test Meeting"
    assert meeting.raw_text.startswith("This meeting")

    loaded = get_meeting(db_session, meeting.id)
    assert loaded is not None
    assert loaded.id == meeting.id
    assert loaded.title == meeting.title


def test_create_meeting_with_action_items(db_session):
    payload = MeetingCreate(
        title="Action Item Meeting",
        raw_text="Discussed tasks and follow-ups.",
        summary="Summary with action items.",
        action_items=[
            {"task": "Send follow-up email", "owner": "Jane Doe", "status": "pending"}
        ]
    )
    meeting = create_meeting(db_session, payload)

    assert meeting.action_items is not None
    assert len(meeting.action_items) == 1
    assert meeting.action_items[0].task == "Send follow-up email"


def test_delete_meeting(db_session):
    payload = MeetingCreate(
        title="Delete Test Meeting",
        raw_text="Raw text to delete.",
        summary="Delete summary."
    )
    meeting = create_meeting(db_session, payload)
    deleted = delete_meeting(db_session, meeting.id)

    assert deleted is not None
    assert deleted.id == meeting.id
    assert get_meeting(db_session, meeting.id) is None
