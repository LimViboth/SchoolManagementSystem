import os
import sys
import django
import requests
from bs4 import BeautifulSoup

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

# Get the base URL from command line or use default
base_url = 'http://127.0.0.1:8000'

def test_csrf_protection():
    print("Testing CSRF protection...")
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    # Step 1: Get the login page to get a CSRF token
    login_url = f"{base_url}/accounts/login/"
    response = session.get(login_url)
    if response.status_code != 200:
        print(f"Failed to get login page: {response.status_code}")
        return False
    
    # Parse the CSRF token from the login page
    soup = BeautifulSoup(response.text, 'html.parser')
    csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
    if not csrf_input:
        print("CSRF token not found on login page!")
        return False
    
    csrf_token = csrf_input['value']
    print(f"Got CSRF token: {csrf_token[:10]}...")
    
    # Step 2: Try to access the course registration page
    registration_url = f"{base_url}/students/courses/registration/"
    response = session.get(registration_url)
    if response.status_code != 200:
        print(f"Failed to get registration page: {response.status_code}")
        return False
    
    print("Successfully accessed course registration page")
    
    # Step 3: Try to submit a form without CSRF token (should fail)
    print("\nTesting form submission without CSRF token (should fail)...")
    offering_id = 1  # Assuming there's a course offering with ID 1
    register_url = f"{base_url}/students/courses/register/{offering_id}/"
    
    response = requests.post(register_url, data={})  # New session without CSRF token
    if response.status_code == 403:
        print("CSRF protection working correctly! Form submission without token was rejected.")
        return True
    else:
        print(f"CSRF protection might not be working. Got status code: {response.status_code}")
        return False

if __name__ == "__main__":
    test_csrf_protection()