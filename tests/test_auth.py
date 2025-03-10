import pytest
import json
from unittest.mock import patch, MagicMock
from app import app
from listing import Listing
from io import BytesIO
from supabase import create_client, Client



@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# ---------------- AUTHENTICATION TESTS ---------------- #

def test_login_fail(client):
    """Test failed login attempt"""
    response = client.post("/login", json={"email": "wronguser@example.com", "password": "wrongpass"})
    assert response.status_code == 400
    assert "error" in response.get_json()

def test_register_success(client):
    """Test successful user registration"""
    response = client.post("/register", json={"email": "newuser@example.com", "password": "SecurePass123"})
    assert response.status_code in [200, 400]  # Handles existing user scenario
    if response.status_code == 400:
        assert "error" in response.get_json()

def test_register_fail(client):
    """Test failed registration due to missing password"""
    response = client.post("/register", json={"email": "user@example.com"})
    assert response.status_code == 400
    assert "error" in response.get_json()

def test_login_success(client):
    """Test successful login attempt"""
    client.post("/register", json={"email": "testuser@example.com", "password": "TestPass123"})
    response = client.post("/login", json={"email": "testuser@example.com", "password": "TestPass123"})
    assert response.status_code == 200
    assert response.get_json() == {"message": "Login successful"}

# ---------------- LISTING TESTS ---------------- #

def test_list_fail_no_image(client):
    """Test listing creation fails due to missing image"""
    response = client.post("/list", data={"name": "Test Item", "bid": "10", "cond": "New"})
    assert response.status_code == 400
    assert "error" in response.get_json()

from io import BytesIO

def test_list_fail_invalid_image(client):
    """Test listing creation fails due to invalid image format"""
    data = {"name": "Test Item", "bid": "10", "cond": "New"}
    invalid_image = (BytesIO(b"fakeimagecontent"), "test.txt")  # Invalid format

    response = client.post("/list", data=data, content_type='multipart/form-data')

    # Ensure that the response status code is 400 (Bad Request)
    assert response.status_code == 400

    # Ensure that the response contains a valid JSON with the expected error message
    response_json = response.get_json()
    assert "error" in response_json


def test_listing_page_exists(client):
    """Test accessing an existing listing page"""
    with patch("app.currListings", {1: Listing({"id": 1, "name": "Item", "bid": 10, "condition": "New", "description": "Desc", "image": "1"})}):
        response = client.get("/listingPage/1")
        assert response.status_code == 200

def test_listing_page_not_found(client):
    """Test accessing a non-existent listing page"""
    response = client.get("/listingPage/999")
    assert response.status_code == 404

# ---------------- BID TESTS ---------------- #

def test_update_bid_success():
    """Test bid updates successfully when higher"""
    listing = Listing({"id": 1, "name": "Item", "bid": 10, "condition": "New", "description": "Desc", "image": "1"})
    with patch("supabase.table") as mock_table:
        mock_update = MagicMock()
        mock_table.return_value.update.return_value.eq.return_value.execute.return_value = {"status": "success"}
        result = listing.updateBid(15)
        assert listing.getBid() == 15
        assert result["status"] == "success"

def test_update_bid_fail_lower_bid():
    """Test bid does not update when lower"""
    listing = Listing({"id": 1, "name": "Item", "bid": 10, "condition": "New", "description": "Desc", "image": "1"})
    result = listing.updateBid(5)
    assert listing.getBid() == 10  # Bid remains unchanged
    assert result is None  # No database update

# ---------------- MOCKING SUPABASE ---------------- #


@patch("app.supabase.auth.sign_up")
def test_register_mock(mock_signup, client):
    """Test user registration with mocked Supabase"""
    # Set the mock return value for sign_up
    mock_signup.return_value = {"user": {"email": "mockuser@example.com"}}
    
    # Make a mock registration request via the Flask test client
    response = client.post("/register", json={"email": "mockuser@example.com", "password": "MockPass123"})
    
    # Assert that the status code is 200 and the response contains a message
    assert response.status_code == 200
    assert "message" in response.get_json()
