import copy

import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture(autouse=True)
def reset_activities():
    original = copy.deepcopy(app_module.activities)
    app_module.activities.clear()
    app_module.activities.update(original)
    yield
    app_module.activities.clear()
    app_module.activities.update(original)


@pytest.fixture()
def client():
    return TestClient(app_module.app)


def test_get_activities_returns_activities(client):
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data


def test_signup_for_activity_adds_participant(client):
    email = "newstudent@example.com"
    response = client.post(
        "/activities/Programming Class/signup",
        params={"email": email},
    )
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Programming Class"

    activities = client.get("/activities").json()
    assert email in activities["Programming Class"]["participants"]


def test_unregister_for_activity_removes_participant(client):
    email = "student@example.com"
    signup_response = client.post(
        "/activities/Art Studio/signup",
        params={"email": email},
    )
    assert signup_response.status_code == 200

    unregister_response = client.post(
        "/activities/Art Studio/unregister",
        params={"email": email},
    )
    assert unregister_response.status_code == 200
    assert unregister_response.json()["message"] == f"Removed {email} from Art Studio"

    activities = client.get("/activities").json()
    assert email not in activities["Art Studio"]["participants"]


def test_signup_for_unknown_activity_returns_not_found(client):
    response = client.post(
        "/activities/Unknown/signup",
        params={"email": "student@example.com"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
