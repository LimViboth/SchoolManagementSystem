import os
import django

# Set up Django first, before importing any models
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

# Now import models and other Django components
from django.test import RequestFactory
from django.contrib.auth.models import User
from core.views import home_view
from teachers.models import Teacher

# Create a request factory
factory = RequestFactory()

# Create a test request
request = factory.get('/')

# Test with an authenticated teacher user
try:
    # Get a teacher
    teacher = Teacher.objects.first()
    if teacher:
        # Set the user on the request
        request.user = teacher.user
        
        # Call the view
        response = home_view(request)
        print("Success! The home_view function executed without errors.")
    else:
        print("No teachers found in the database.")
except AttributeError as e:
    print(f"AttributeError: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")