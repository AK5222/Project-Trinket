import pytest
import json
from unittest.mock import patch, MagicMock
from io import BytesIO
from app import app, supabase, createListing, fetchNewListings, processListings
from listing import Listing  # Import the Listing class
from app import currListings
from datetime import datetime, timezone
import os

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_supabase():
    with patch('app.supabase') as mock:
        yield mock

# ---------------- AUTHENTICATION TESTS ---------------- #

def test_register_success(client, mock_supabase):
    mock_supabase.auth.sign_up.return_value = {"user": {"email": "newuser@example.com"}}
    response = client.post("/register", json={"email": "newuser@example.com", "password": "SecurePass123"})
    assert response.status_code == 200
    assert "message" in response.get_json()

def test_login_success(client, mock_supabase):
    mock_supabase.auth.sign_in_with_password.return_value = {"user": {"email": "testuser@example.com"}}
    response = client.post("/login", json={"email": "testuser@example.com", "password": "TestPass123"})
    assert response.status_code == 200
    assert response.get_json() == {"message": "Login successful"}

# ---------------- LISTING TESTS ---------------- #

def test_list_success(client, mock_supabase):
    mock_supabase.table().insert().execute.return_value = MagicMock(data=[{'id': 1}])
    mock_supabase.storage.from_().upload.return_value = True

    data = {
        "name": "Test Item",
        "bid": "10",
        "cond": "New",
        "desc": "Test description"
    }
    image = (BytesIO(b"fakeimagecontent"), "test_image.png")

    response = client.post("/list", data={**data, "image": image}, content_type='multipart/form-data')
    assert response.status_code == 200

def test_listing_page_exists(client, mock_supabase):
    listing_data = {"id": 1, "name": "Item", "bid": 10, "condition": "New", "description": "Desc", "image": "1.jpg"}
    mock_supabase.storage.from_().create_signed_url.return_value = {'signedUrl': 'http://example.com/image.jpg'}
    with patch.dict(currListings, {1: Listing(listing_data)}):
        response = client.get("/listingPage/1")
        assert response.status_code == 200

# ---------------- LISTING CLASS TESTS ---------------- #

def test_listing_creation(mock_supabase):
    listing_data = {"id": 1, "name": "Item", "bid": 10, "condition": "New", "description": "Desc", "image": "1.jpg"}
    mock_supabase.storage.from_('images').create_signed_url.return_value = {'signedUrl': 'http://example.com/image.jpg'}
    listing_obj = Listing(listing_data)
    assert listing_obj.getName() == "Item"
    assert listing_obj.getBid() == 10
    assert listing_obj.getCondition() == "New"
    assert listing_obj.getURL() == 'http://example.com/image.jpg'

def test_listing_update_bid(mock_supabase):
    listing_data = {"id": 1, "name": "Item", "bid": 10, "condition": "New", "description": "Desc", "image": "1.jpg"}
    mock_supabase.storage.from_().create_signed_url.return_value = {'signedUrl': 'http://example.com/image.jpg'}
    mock_supabase.table().update().eq().execute.return_value = {"status": "success"}
    listing_obj = Listing(listing_data)
    result = listing_obj.updateBid(15)
    assert listing_obj.getBid() == 15  # Bid should be updated locally
    assert result == {"status": "success"}  # Check if the Supabase update was called

def test_listing_update_bid_fail(mock_supabase):
    listing_data = {"id": 1, "name": "Item", "bid": 10, "condition": "New", "description": "Desc", "image": "1.jpg"}
    mock_supabase.storage.from_().create_signed_url.return_value = {'signedUrl': 'http://example.com/image.jpg'}
    listing_obj = Listing(listing_data)
    result = listing_obj.updateBid(5)
    assert listing_obj.getBid() == 10  # Bid should not be updated
    assert result is None

# ---------------- HELPER FUNCTION TESTS ---------------- #

def test_create_listing(mock_supabase):
    mock_supabase.table().insert().execute.return_value = MagicMock(data=[{'id': 1}])
    response = createListing("Test Item", 10, "New", "Description", "image.jpg")
    assert response is not None

def test_fetch_new_listings(mock_supabase):
    mock_response = MagicMock()
    mock_response.data = [{"id": 1, "name": "Item"}]
    mock_supabase.table().select().gte().execute.return_value = mock_response
    response = fetchNewListings()
    assert response.data == [{"id": 1, "name": "Item"}]

def test_process_listings(mock_supabase):
    mock_supabase.table().select().lte().execute.return_value = MagicMock(data=[{"image": "1.jpg"}])
    with patch('app.updateListings') as mock_update:
        processListings()
        mock_update.assert_called_once()

# ---------------- SCHEDULING TESTS ---------------- #

def test_time_left():
    from app import timeLeft
    seconds = timeLeft()
    assert 0 <= seconds <= 1800  # Between 0 and 30 minutes
