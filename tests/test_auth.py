import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_login_fail(client):
    """Test failed login attempt"""
    response = client.post("/login", json={"email": "wronguser@example.com", "password": "wrongpass"})
    assert response.status_code == 400  # Expecting failure
    assert "error" in response.get_json()

def test_register_success(client):
    """Test successful user registration"""
    response = client.post("/register", json={"email": "newuser@example.com", "password": "SecurePass123"})
    assert response.status_code in [200, 400]  # 200 if successful, 400 if email already exists
    if response.status_code == 400:
        assert "error" in response.get_json()

def test_register_fail(client):
    """Test failed user registration due to missing fields"""
    response = client.post("/register", json={"email": "user@example.com"})  # Missing password
    assert response.status_code == 400  # Expecting failure
    assert "error" in response.get_json()

"""""
def test_login_success(client):
    #Test successful login attempt
    client.post("/register", json={"email": "testuser@example.com", "password": "TestPass123"})  # Ensure user exists
    response = client.post("/login", json={"email": "testuser@example.com", "password": "TestPass123"})
    assert response.status_code == 200  # Expecting success
    assert response.get_json() == {"message": "Login successful"}
"""

def test_list_fail_no_image(client):
    """Test listing creation fails due to missing image"""
    response = client.post("/list", data={"name": "Test Item", "bid": "10", "cond": "New"})
    assert response.status_code == 400  # Expecting failure
    assert "error" in response.get_json()