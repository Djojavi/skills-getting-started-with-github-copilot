import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities as app_activities

client = TestClient(app)

INITIAL_ACTIVITIES = copy.deepcopy(app_activities)


@pytest.fixture(autouse=True)
def reset_activities():
    # Arrange: reset in-memory state for each test to avoid cross-test pollution
    app_activities.clear()
    app_activities.update(copy.deepcopy(INITIAL_ACTIVITIES))
    yield


def test_get_activities_returns_default_data():
    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_for_activity_adds_participant():
    # Arrange
    activity_name = "Chess Club"
    new_email = "testuser@mergington.edu"
    initial_count = len(app_activities[activity_name]["participants"])

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": new_email})

    # Assert
    assert response.status_code == 200
    assert new_email in response.json()["message"]

    check = client.get("/activities").json()
    assert len(check[activity_name]["participants"]) == initial_count + 1
    assert new_email in check[activity_name]["participants"]


def test_signup_duplicate_returns_400():
    # Arrange
    activity_name = "Chess Club"
    existing_email = app_activities[activity_name]["participants"][0]

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": existing_email})

    # Assert
    assert response.status_code == 400


def test_unregister_participant_removes_from_activity():
    # Arrange
    activity_name = "Programming Class"
    participant_email = app_activities[activity_name]["participants"][0]
    start_count = len(app_activities[activity_name]["participants"])

    # Act
    response = client.delete(f"/activities/{activity_name}/participants", params={"email": participant_email})

    # Assert
    assert response.status_code == 200
    assert participant_email in response.json()["message"]

    check = client.get("/activities").json()
    assert len(check[activity_name]["participants"]) == start_count - 1
    assert participant_email not in check[activity_name]["participants"]


def test_unregister_missing_participant_returns_404():
    # Arrange
    activity_name = "Gym Class"
    missing_email = "doesnotexist@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants", params={"email": missing_email})

    # Assert
    assert response.status_code == 404
