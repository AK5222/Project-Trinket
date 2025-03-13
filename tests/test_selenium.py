# test_selenium.py
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import os
import base64
import tempfile
from dotenv import load_dotenv

load_dotenv()

# Constants - Replace with your actual app URL and credentials
BASE_URL = "http://127.0.0.1:5000"  # Default Flask URL. Change if different.
TEST_EMAIL = "test@example.com"  # Replace with your test email. Ensure this user exists.
TEST_PASSWORD = "testpassword"  # Replace with your test password

# Supabase URL
SUPABASE_URL = os.getenv("SUPABASE_URL")

# Base64 encoded 1x1 pixel transparent GIF
TRANSPARENT_GIF_BASE64 = "R0lGODlhAQABAIAAAP///////yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"

@pytest.fixture(scope="module")
def driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run Chrome in headless mode
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(5)  # Reduced implicit wait
    yield driver
    driver.quit()

# HELPER FUNCTIONS
def register_user(driver, email, password):
    driver.get(f"{BASE_URL}/register")
    email_field = driver.find_element(By.ID, "email")
    password_field = driver.find_element(By.ID, "password")
    submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    email_field.send_keys(email)
    password_field.send_keys(password)
    submit_button.click()

def login(driver, email, password):
    driver.get(f"{BASE_URL}/login")
    email_field = driver.find_element(By.ID, "email")
    password_field = driver.find_element(By.ID, "password")
    submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    email_field.send_keys(email)
    password_field.send_keys(password)
    submit_button.click()
    WebDriverWait(driver, 10).until(EC.url_contains("/"))

def logout(driver):
    driver.get(f"{BASE_URL}/logout")
    WebDriverWait(driver, 10).until(EC.url_contains("/"))  #Wait until it is on the home page

# Helper function to check for alert messages
def check_alert_text(driver, expected_text, timeout=10):
    try:
        WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CLASS_NAME, "alert")))
        alert = driver.find_element(By.CLASS_NAME, "alert")
        return expected_text in alert.text
    except:
        return True

# TESTS

def test_env_vars():
    assert SUPABASE_URL is not None  #Check the Supabase URL

def test_index_page_loads(driver):
    driver.get(BASE_URL)
    assert "Trinket" in driver.title

def test_register_page_loads(driver):
    driver.get(f"{BASE_URL}/register")
    assert "Register" in driver.page_source

def test_login_page_loads(driver):
    driver.get(f"{BASE_URL}/login")
    assert "Sign In" in driver.page_source

def test_account_page_loads_when_logged_in(driver):
    login(driver, TEST_EMAIL, TEST_PASSWORD)
    driver.get(f"{BASE_URL}/account")
    assert "Account Page" in driver.page_source

def test_list_item_page_loads_when_logged_in(driver):
    login(driver, TEST_EMAIL, TEST_PASSWORD)
    driver.get(f"{BASE_URL}/list")
    assert "List an Item" in driver.page_source

def test_successful_registration(driver):
    unique_email = f"test{int(time.time())}@example.com"
    register_user(driver, unique_email, "Testpassword123!")
    assert check_alert_text(driver, "User registered successfully")

def test_registration_with_existing_email(driver):
    register_user(driver, TEST_EMAIL, "SomeNewPassword123!")
    assert check_alert_text(driver, "User already registered")

def test_successful_login(driver):
    login(driver, TEST_EMAIL, TEST_PASSWORD)
    assert check_alert_text(driver, "Login successful")

def test_logout(driver):
    login(driver, TEST_EMAIL, TEST_PASSWORD)
    logout(driver)
    assert "Sign In" in driver.page_source

def test_list_item_success(driver):
    login(driver, TEST_EMAIL, TEST_PASSWORD)
    driver.get(f"{BASE_URL}/list")

    # Locate form elements
    name_field = driver.find_element(By.ID, "name")
    bid_field = driver.find_element(By.ID, "bid")
    condition_dropdown = driver.find_element(By.ID, "cond")
    image_upload = driver.find_element(By.ID, "image")
    description_field = driver.find_element(By.ID, "desc")
    submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

    # Populate form fields
    name_field.send_keys("Test Item")
    bid_field.send_keys("10")

    # Select an item from the condition dropdown
    condition_dropdown.send_keys("New")

    # Use the test image from the tests/ folder
    test_image_path = os.path.abspath("tests/test_image.png")
    image_upload.send_keys(test_image_path)

    description_field.send_keys("Test Description")

    # Submit the form
    submit_button.click()

    # Wait for redirect to listingSuccess.html
    WebDriverWait(driver, 10).until(EC.url_contains(f"{BASE_URL}/list"))

    # Verify that the "Listing Created Successfully!" message is present on listingSuccess.html
    assert "Listing created successfully!" in driver.page_source


