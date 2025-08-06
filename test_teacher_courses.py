import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

# Import models
from teachers.models import Teacher
from courses.models import CourseOffering

# Test if Teacher model has teaching_courses attribute
try:
    # Get a teacher
    teacher = Teacher.objects.first()
    if teacher:
        # Try to access teaching_courses
        courses = teacher.teaching_courses.all()
        print(f"Success! Teacher {teacher} has {courses.count()} teaching courses.")
    else:
        print("No teachers found in the database.")
except AttributeError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")