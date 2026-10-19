import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def basketball_participants():
    activity = activities["Basketball Club"]
    original_participants = activity["participants"]
    activity["participants"] = []
    yield activity["participants"]
    activity["participants"] = original_participants


def test_get_activities_returns_activity_details(client):
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json()["Chess Club"]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]
    assert response.json()["Basketball Club"]["participants"] == []


def test_signup_adds_participant(client, basketball_participants):
    email = "student@mergington.edu"

    response = client.post(
        "/activities/Basketball%20Club/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for Basketball Club"
    }
    assert email in client.get("/activities").json()["Basketball Club"]["participants"]


def test_signup_rejects_duplicate_participant(client, basketball_participants):
    email = "student@mergington.edu"
    basketball_participants.append(email)

    response = client.post(
        "/activities/Basketball%20Club/signup",
        params={"email": email},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
    assert basketball_participants == [email]


def test_signup_rejects_unknown_activity(client, basketball_participants):
    response = client.post(
        "/activities/Unknown%20Activity/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant(client, basketball_participants):
    email = "student@mergington.edu"
    basketball_participants.append(email)

    response = client.delete(
        "/activities/Basketball%20Club/participants",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Removed {email} from Basketball Club"
    }
    assert email not in client.get("/activities").json()["Basketball Club"]["participants"]


def test_remove_rejects_unregistered_participant(client, basketball_participants):
    response = client.delete(
        "/activities/Basketball%20Club/participants",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_remove_rejects_unknown_activity(client, basketball_participants):
    response = client.delete(
        "/activities/Unknown%20Activity/participants",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
