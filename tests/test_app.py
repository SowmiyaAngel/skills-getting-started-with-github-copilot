import copy

from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)


def setup_function():
    """Restore activities state before each test."""
    global original_activities
    original_activities = copy.deepcopy(activities)


def teardown_function():
    """Reset activities state after each test."""
    activities.clear()
    activities.update(copy.deepcopy(original_activities))


def test_root_redirects_to_static_index_html():
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_get_activities_returns_activity_data():
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    json_data = response.json()
    assert expected_activity in json_data
    assert "description" in json_data[expected_activity]
    assert "participants" in json_data[expected_activity]


def test_signup_for_activity_adds_participant():
    # Arrange
    activity_name = "Programming Class"
    email = "newstudent@mergington.edu"
    assert email not in activities[activity_name]["participants"]

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate_returns_400():
    # Arrange
    activity_name = "Chess Club"
    duplicate_email = activities[activity_name]["participants"][0]

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": duplicate_email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant_removes_existing_participant():
    # Arrange
    activity_name = "Basketball Team"
    email = activities[activity_name]["participants"][0]
    assert email in activities[activity_name]["participants"]

    # Act
    response = client.delete(f"/activities/{activity_name}/participant", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]


def test_remove_missing_participant_returns_404():
    # Arrange
    activity_name = "Drama Club"
    missing_email = "missing@student.edu"
    assert missing_email not in activities[activity_name]["participants"]

    # Act
    response = client.delete(f"/activities/{activity_name}/participant", params={"email": missing_email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_signup_unknown_activity_returns_404():
    # Arrange
    activity_name = "Nonexistent Club"
    email = "unknown@student.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_unknown_activity_returns_404():
    # Arrange
    activity_name = "Nonexistent Club"
    email = "unknown@student.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participant", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
