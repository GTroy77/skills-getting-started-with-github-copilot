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


def test_unregister_participant_from_activity(client):
    signup_response = client.post(
        "/activities/Chess Club/signup?email=student@example.com"
    )
    assert signup_response.status_code == 200

    unregister_response = client.post(
        "/activities/Chess Club/unregister?email=student@example.com"
    )
    assert unregister_response.status_code == 200

    activities = client.get("/activities").json()
    assert "student@example.com" not in activities["Chess Club"]["participants"]


def test_unregister_unknown_participant_returns_not_found(client):
    response = client.post(
        "/activities/Chess Club/unregister?email=missing@example.com"
    )
    assert response.status_code == 404
