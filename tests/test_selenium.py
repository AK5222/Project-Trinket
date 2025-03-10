import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time

# Setup and Teardown for WebDriver
@pytest.fixture(scope="module")
def driver():
    # Setup: Start ChromeDriver
    driver = webdriver.Chrome()
    driver.get("http://localhost:5000")  # Replace with your app's local URL if different
    yield driver  # The tests will run here
    # Teardown: Close WebDriver
    driver.quit()

# 1. Test Navigation Bar and Links
def test_navigation_bar(driver):
    # Test all the links in the navigation bar
    nav_links = [
        ("/login", "Sign In"),
        ("/account", "Account"),
        ("/list", "List Item"),
        ("/", "Home")
    ]
    
    for link, link_text in nav_links:
        link_element = driver.find_element(By.LINK_TEXT, link_text)
        link_element.click()
        time.sleep(1)  # Wait for page load
        assert driver.current_url.endswith(link)  # Check the URL is correct
        driver.back()  # Go back to the previous page

# 2. Test Create Account / Register Form
def test_register_form(driver):
    driver.get("http://localhost:5000/register")
    email_input = driver.find_element(By.ID, "email")
    password_input = driver.find_element(By.ID, "password")
    submit_button = driver.find_element(By.XPATH, "//button[text()='Register']")
    
    # Test with valid data
    email_input.send_keys("achac021@ucr.edu")
    password_input.send_keys("SecurePassword123")
    submit_button.click()
    time.sleep(2)
    assert "Login" in driver.page_source  # Assuming it redirects to login page after successful registration

    # Test with invalid email format
    email_input.clear()
    email_input.send_keys("invalid-email")
    password_input.clear()
    password_input.send_keys("Password123")
    submit_button.click()
    time.sleep(2)
    assert "Invalid email" in driver.page_source  # Assuming the page shows an error message for invalid email

# 3. Test Login Page
def test_login(driver):
    driver.get("http://localhost:5000/login")
    email_input = driver.find_element(By.ID, "email")
    password_input = driver.find_element(By.ID, "password")
    login_button = driver.find_element(By.XPATH, "//button[text()='Login']")
    
    # Test valid login
    email_input.send_keys("testuser@example.com")
    password_input.send_keys("SecurePassword123")
    login_button.click()
    time.sleep(2)
    assert "Account" in driver.page_source  # Assuming it redirects to the account page after successful login

    # Test invalid login
    email_input.clear()
    email_input.send_keys("wrongemail@example.com")
    password_input.clear()
    password_input.send_keys("WrongPassword")
    login_button.click()
    time.sleep(2)
    assert "Invalid login" in driver.page_source  # Assuming it shows an error for invalid login

# 4. Test Account Page
def test_account_page(driver):
    driver.get("http://localhost:5000/account")
    # Ensure that the account page shows the correct information
    assert "Account page" in driver.page_source  # Check for the text inside the account page
    assert "Idk what to do with this" in driver.page_source  # Check for the placeholder text

# 5. Test Listing Creation Form
def test_create_listing(driver):
    driver.get("http://localhost:5000/list")
    
    name_input = driver.find_element(By.ID, "name")
    bid_input = driver.find_element(By.ID, "bid")
    condition_select = driver.find_element(By.ID, "cond")
    description_input = driver.find_element(By.ID, "desc")
    image_input = driver.find_element(By.ID, "image")
    submit_button = driver.find_element(By.XPATH, "//button[text()='Submit Listing']")
    
    # Test creating a valid listing
    name_input.send_keys("Test Item")
    bid_input.send_keys("10")
    condition_select.send_keys("new")
    description_input.send_keys("A brand new test item.")
    image_input.send_keys("/path/to/sample-image.jpg")  # Provide the correct image file path
    submit_button.click()
    time.sleep(2)
    assert "Listing created successfully" in driver.page_source  # Check for the success message

    # Test submitting with empty required fields
    name_input.clear()
    bid_input.clear()
    submit_button.click()
    time.sleep(2)
    assert "This field is required" in driver.page_source  # Check for error if required fields are missing

# 6. Test Listing Details Page
def test_listing_page(driver):
    driver.get("http://localhost:5000")
    listing_link = driver.find_element(By.XPATH, "//a[contains(@href, '/listingPage')]")
    listing_link.click()
    time.sleep(2)
    
    # Test that the listing details are correctly displayed
    assert "Test Item" in driver.page_source
    assert "Condition: new" in driver.page_source
    assert "A brand new test item." in driver.page_source

# 7. Test Listing Success Page
def test_listing_success(driver):
    driver.get("http://localhost:5000/listingSuccess")
    assert "Listing created successfully!" in driver.page_source

# 8. Test Password Reset Page
def test_password_reset(driver):
    driver.get("http://localhost:5000/resetPassword")
    assert "Password will be reset here eventually" in driver.page_source

# 9. Test Payment Method Page
def test_payment_method(driver):
    driver.get("http://localhost:5000/PaymentMethod")
    
    cardholder_input = driver.find_element(By.ID, "cardholderName")
    cardnumber_input = driver.find_element(By.ID, "cardNumber")
    expiry_input = driver.find_element(By.ID, "expiryDate")
    cvv_input = driver.find_element(By.ID, "cvv")
    submit_button = driver.find_element(By.XPATH, "//button[text()='Submit Payment']")
    
    # Test valid payment details
    cardholder_input.send_keys("John Doe")
    cardnumber_input.send_keys("1234567890123456")
    expiry_input.send_keys("12/25")
    cvv_input.send_keys("123")
    submit_button.click()
    time.sleep(2)
    assert "Payment submitted" in driver.page_source  # Assuming success message for payment

    # Test invalid payment details
    cardholder_input.clear()
    cardnumber_input.clear()
    submit_button.click()
    time.sleep(2)
    assert "This field is required" in driver.page_source  # Check for error when submitting empty fields

