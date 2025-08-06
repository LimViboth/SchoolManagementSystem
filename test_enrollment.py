"""
Test script to verify the enrollment process and check for duplicate enrollment handling.
"""
import os
import django
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from courses.models import CourseOffering, Enrollment
from students.models import Student
from django.db import IntegrityError

def test_enrollment_process():
    """Test the enrollment process and duplicate enrollment handling"""
    print("Testing enrollment process and duplicate enrollment handling...")
    
    # Get a student and course offering for testing
    # Using the IDs from the error message: student_id=156, course_offering_id=84
    try:
        student = Student.objects.get(id=156)
        course_offering = CourseOffering.objects.get(id=84)
    except (Student.DoesNotExist, CourseOffering.DoesNotExist):
        # If the specific IDs don't exist, get any student and course offering
        student = Student.objects.first()
        course_offering = CourseOffering.objects.first()
        
        if not student or not course_offering:
            print("No students or course offerings found in the database.")
            return
    
    print(f"\nTesting with Student ID: {student.id}, Course Offering ID: {course_offering.id}")
    
    # Check if enrollment already exists
    existing_active = Enrollment.objects.filter(
        student=student,
        course_offering=course_offering,
        withdrawn=False
    ).exists()
    
    existing_withdrawn = Enrollment.objects.filter(
        student=student,
        course_offering=course_offering,
        withdrawn=True
    ).exists()
    
    print(f"Active enrollment exists: {existing_active}")
    print(f"Withdrawn enrollment exists: {existing_withdrawn}")
    
    # Test case 1: Try to create a new enrollment
    print("\nTest case 1: Creating a new enrollment")
    try:
        # First, make sure there's no active enrollment
        Enrollment.objects.filter(
            student=student,
            course_offering=course_offering
        ).delete()
        
        # Create a new enrollment
        enrollment = Enrollment.objects.create(
            student=student,
            course_offering=course_offering
        )
        print("Successfully created new enrollment")
        
        # Clean up - delete the enrollment
        enrollment.delete()
    except IntegrityError as e:
        print(f"IntegrityError: {e}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test case 2: Try to create a duplicate enrollment
    print("\nTest case 2: Creating a duplicate enrollment")
    try:
        # Create first enrollment
        enrollment1 = Enrollment.objects.create(
            student=student,
            course_offering=course_offering
        )
        print("Successfully created first enrollment")
        
        # Try to create a duplicate enrollment
        enrollment2 = Enrollment.objects.create(
            student=student,
            course_offering=course_offering
        )
        print("Successfully created second enrollment (this should not happen)")
        
        # Clean up
        enrollment1.delete()
        enrollment2.delete()
    except IntegrityError as e:
        print(f"IntegrityError (expected): {e}")
        
        # Clean up
        Enrollment.objects.filter(
            student=student,
            course_offering=course_offering
        ).delete()
    except Exception as e:
        print(f"Error: {e}")
    
    # Test case 3: Withdrawn enrollment handling
    print("\nTest case 3: Withdrawn enrollment handling")
    try:
        # Create an enrollment and mark it as withdrawn
        enrollment = Enrollment.objects.create(
            student=student,
            course_offering=course_offering
        )
        enrollment.withdrawn = True
        enrollment.save()
        print("Created withdrawn enrollment")
        
        # Try to create a new enrollment for the same student and course
        try:
            new_enrollment = Enrollment.objects.create(
                student=student,
                course_offering=course_offering
            )
            print("Successfully created new enrollment despite withdrawn enrollment existing")
            
            # Clean up
            enrollment.delete()
            new_enrollment.delete()
        except IntegrityError as e:
            print(f"IntegrityError: {e}")
            print("This confirms that even withdrawn enrollments cause unique constraint violations")
            
            # Clean up
            enrollment.delete()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_enrollment_process()