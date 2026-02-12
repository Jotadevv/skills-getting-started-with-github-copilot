"""Tests for the Mergington High School Activities API"""

import pytest


class TestGetActivities:
    """Tests for the GET /activities endpoint"""

    def test_get_activities_returns_200(self, client):
        """Test that GET /activities returns a 200 status code"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self, client):
        """Test that GET /activities returns a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)

    def test_get_activities_contains_expected_activities(self, client):
        """Test that GET /activities contains expected activity names"""
        response = client.get("/activities")
        activities = response.json()
        
        expected_activities = [
            "Tennis Club", "Basketball Team", "Art Studio", "Music Ensemble",
            "Debate Team", "Science Club", "Chess Club", "Programming Class", "Gym Class"
        ]
        
        for activity in expected_activities:
            assert activity in activities

    def test_get_activities_structure(self, client):
        """Test that each activity has the expected structure"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Tennis Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]

    def test_signup_adds_participant(self, client):
        """Test that signup actually adds the participant to the activity"""
        email = "participant@mergington.edu"
        
        # Sign up for Tennis Club
        client.post("/activities/Tennis Club/signup", params={"email": email})
        
        # Verify participant was added
        response = client.get("/activities")
        activities = response.json()
        assert email in activities["Tennis Club"]["participants"]

    def test_signup_duplicate_email_rejected(self, client):
        """Test that a student cannot sign up twice for the same activity"""
        email = "alex@mergington.edu"  # Already signed up for Tennis Club
        
        response = client.post(
            "/activities/Tennis Club/signup",
            params={"email": email}
        )
        
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_nonexistent_activity(self, client):
        """Test that signup fails for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Club/signup",
            params={"email": "student@mergington.edu"}
        )
        
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_multiple_activities(self, client):
        """Test that a student can sign up for multiple different activities"""
        email = "multistudent@mergington.edu"
        
        # Sign up for two different activities
        response1 = client.post("/activities/Tennis Club/signup", params={"email": email})
        response2 = client.post("/activities/Art Studio/signup", params={"email": email})
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verify student is in both activities
        response = client.get("/activities")
        activities = response.json()
        assert email in activities["Tennis Club"]["participants"]
        assert email in activities["Art Studio"]["participants"]

    def test_signup_email_case_sensitivity(self, client):
        """Test signup behavior with different email cases"""
        email1 = "student@mergington.edu"
        email2 = "STUDENT@MERGINGTON.EDU"
        
        # Sign up with lowercase
        response1 = client.post("/activities/Tennis Club/signup", params={"email": email1})
        assert response1.status_code == 200
        
        # Try to sign up with uppercase (exact match should work, but different strings)
        response2 = client.post("/activities/Tennis Club/signup", params={"email": email2})
        # This will succeed because Python treats them as different strings
        assert response2.status_code == 200

    def test_signup_empty_email(self, client):
        """Test that empty email is handled"""
        response = client.post(
            "/activities/Tennis Club/signup",
            params={"email": ""}
        )
        # FastAPI will still pass empty string, server accepts it
        # This tests current behavior - could be improved with validation
        assert response.status_code == 200

    def test_signup_special_characters_email(self, client):
        """Test signup with special characters in email"""
        email = "student+test@mergington.edu"
        
        response = client.post(
            "/activities/Tennis Club/signup",
            params={"email": email}
        )
        
        assert response.status_code == 200
        response = client.get("/activities")
        assert email in response.json()["Tennis Club"]["participants"]


class TestUnregisterFromActivity:
    """Tests for the POST /activities/{activity_name}/unregister endpoint"""

    def test_unregister_success(self, client):
        """Test successful unregistration from an activity"""
        email = "alex@mergington.edu"  # Already in Tennis Club
        
        response = client.post(
            "/activities/Tennis Club/unregister",
            params={"email": email}
        )
        
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]

    def test_unregister_removes_participant(self, client):
        """Test that unregister actually removes the participant"""
        email = "james@mergington.edu"  # In Basketball Team
        
        # Unregister
        client.post("/activities/Basketball Team/unregister", params={"email": email})
        
        # Verify participant was removed
        response = client.get("/activities")
        activities = response.json()
        assert email not in activities["Basketball Team"]["participants"]

    def test_unregister_not_signed_up(self, client):
        """Test that unregister fails for student not signed up"""
        email = "notstudent@mergington.edu"
        
        response = client.post(
            "/activities/Tennis Club/unregister",
            params={"email": email}
        )
        
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_unregister_nonexistent_activity(self, client):
        """Test that unregister fails for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Club/unregister",
            params={"email": "student@mergington.edu"}
        )
        
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_after_unregister(self, client):
        """Test that a student can sign up again after unregistering"""
        email = "reusable@mergington.edu"
        activity = "Tennis Club"
        
        # Sign up
        response1 = client.post(f"/activities/{activity}/signup", params={"email": email})
        assert response1.status_code == 200
        
        # Unregister
        response2 = client.post(f"/activities/{activity}/unregister", params={"email": email})
        assert response2.status_code == 200
        
        # Sign up again
        response3 = client.post(f"/activities/{activity}/signup", params={"email": email})
        assert response3.status_code == 200
        
        # Verify student is signed up
        response = client.get("/activities")
        assert email in response.json()[activity]["participants"]



class TestIntegration:
    """Integration tests for the activities API"""

    def test_signup_updates_activities_endpoint(self, client):
        """Test that activities endpoint reflects signup changes immediately"""
        email = "integration@mergington.edu"
        activity = "Basketball Team"
        
        # Get initial participant count
        response1 = client.get("/activities")
        initial_count = len(response1.json()[activity]["participants"])
        
        # Sign up
        signup_response = client.post(f"/activities/{activity}/signup", params={"email": email})
        assert signup_response.status_code == 200
        
        # Verify participant count increased
        response2 = client.get("/activities")
        new_count = len(response2.json()[activity]["participants"])
        assert new_count == initial_count + 1
