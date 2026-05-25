

def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome to" in response.json()["message"]


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_generate_and_read_meeting(client):
    payload = {
        "title": "Endpoint Test Meeting",
        "raw_text": "Review project requirements and next steps.",
        "summary": "A short summary of the endpoint test."
    }
    response = client.post("/generate", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["raw_text"] == payload["raw_text"]

    meeting_id = data["id"]
    get_response = client.get(f"/meeting/{meeting_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == meeting_id


def test_delete_meeting_route(client):
    payload = {
        "title": "Delete Route Meeting",
        "raw_text": "Meeting to delete via route.",
        "summary": "Delete route summary."
    }
    response = client.post("/generate", json=payload)
    assert response.status_code == 201

    meeting_id = response.json()["id"]
    delete_response = client.delete(f"/meeting/{meeting_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["detail"] == "Meeting deleted successfully"

    missing_response = client.get(f"/meeting/{meeting_id}")
    assert missing_response.status_code == 404


def test_update_action_item_route(client):
    payload = {
        "title": "Action Item Update Meeting",
        "raw_text": "Meeting with an action item to update.",
        "summary": "Action item update summary.",
        "action_items": [
            {"task": "Send summary email", "owner": "Sam", "status": "pending"}
        ]
    }
    create_response = client.post("/generate", json=payload)
    assert create_response.status_code == 201
    meeting_data = create_response.json()
    assert meeting_data["action_items"]

    action_item = meeting_data["action_items"][0]
    update_data = {"status": "completed"}
    update_response = client.put(f"/action-item/{action_item['id']}", json=update_data)
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "completed"
