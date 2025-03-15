import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


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