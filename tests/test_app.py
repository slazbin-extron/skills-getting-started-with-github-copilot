import copy
import pytest
from fastapi.testclient import TestClient
import app as app_module
from app import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the activities dict to its original state after each test."""
    original = copy.deepcopy(app_module.activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(original)


# ---------------------------------------------------------------------------
# GET /activities
# ---------------------------------------------------------------------------

def test_get_activities_returns_200():
    response = client.get("/activities")
    assert response.status_code == 200


def test_get_activities_returns_dict():
    response = client.get("/activities")
    data = response.json()
    assert isinstance(data, dict)


def test_get_activities_contains_expected_keys():
    response = client.get("/activities")
    data = response.json()
    expected_activities = [
        "Chess Club",
        "Programming Class",
        "Gym Class",
        "Soccer Team",
        "Basketball Club",
        "Art Club",
        "Drama Society",
        "Mathletes",
        "Science Club",
    ]
    for name in expected_activities:
        assert name in data, f"Expected activity '{name}' not found"


def test_get_activities_each_has_required_fields():
    response = client.get("/activities")
    for name, details in response.json().items():
        assert "description" in details, f"'{name}' missing 'description'"
        assert "schedule" in details, f"'{name}' missing 'schedule'"
        assert "max_participants" in details, f"'{name}' missing 'max_participants'"
        assert "participants" in details, f"'{name}' missing 'participants'"


# ---------------------------------------------------------------------------
# POST /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

def test_signup_success():
    response = client.post("/activities/Soccer Team/signup", params={"email": "new@mergington.edu"})
    assert response.status_code == 200
    assert "new@mergington.edu" in response.json()["message"]


def test_signup_adds_participant():
    client.post("/activities/Soccer Team/signup", params={"email": "new@mergington.edu"})
    response = client.get("/activities")
    assert "new@mergington.edu" in response.json()["Soccer Team"]["participants"]


def test_signup_already_signed_up_returns_400():
    email = "michael@mergington.edu"  # already in Chess Club
    response = client.post("/activities/Chess Club/signup", params={"email": email})
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()


def test_signup_unknown_activity_returns_404():
    response = client.post("/activities/Nonexistent Club/signup", params={"email": "x@mergington.edu"})
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


# ---------------------------------------------------------------------------
# DELETE /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

def test_unregister_success():
    email = "michael@mergington.edu"  # existing participant in Chess Club
    response = client.delete("/activities/Chess Club/signup", params={"email": email})
    assert response.status_code == 200
    assert email in response.json()["message"]


def test_unregister_removes_participant():
    email = "michael@mergington.edu"
    client.delete("/activities/Chess Club/signup", params={"email": email})
    response = client.get("/activities")
    assert email not in response.json()["Chess Club"]["participants"]


def test_unregister_not_signed_up_returns_404():
    response = client.delete("/activities/Chess Club/signup", params={"email": "nobody@mergington.edu"})
    assert response.status_code == 404
    assert "not signed up" in response.json()["detail"].lower()


def test_unregister_unknown_activity_returns_404():
    response = client.delete("/activities/Nonexistent Club/signup", params={"email": "x@mergington.edu"})
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
