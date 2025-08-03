"""
Test script to verify the increased course capacity functionality.
"""
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from courses.models import CourseOffering, Enrollment
from students.models import Student
from django.db.models import Count

def test_course_capacity():
    """Test the course capacity functionality"""
    print("Testing course capacity functionality...")
    
    # Get all course offerings
    offerings = CourseOffering.objects.all()
    
    print(f"Found {offerings.count()} course offerings")
    
    for offering in offerings:
        # Count enrollments
        enrolled_count = Enrollment.objects.filter(
            course_offering=offering,
            withdrawn=False
        ).count()
        
        # Calculate original and increased capacity
        original_capacity = offering.max_students
        increased_capacity = int(original_capacity * 1.2)
        available_slots = increased_capacity - enrolled_count
        
        print(f"\nCourse: {offering.course.code} - {offering.course.name}")
        print(f"Original capacity: {original_capacity}")
        print(f"Increased capacity (20%): {increased_capacity}")
        print(f"Current enrollments: {enrolled_count}")
        print(f"Available slots with original capacity: {original_capacity - enrolled_count}")
        print(f"Available slots with increased capacity: {available_slots}")
        
        # Check if the course would be full without increased capacity
        if enrolled_count >= original_capacity:
            print("Status with original capacity: FULL")
        else:
            print("Status with original capacity: Available")
            
        # Check if the course is full with increased capacity
        if enrolled_count >= increased_capacity:
            print("Status with increased capacity: FULL")
        else:
            print("Status with increased capacity: Available")
            
        # Calculate how many more students can enroll with increased capacity
        additional_spots = increased_capacity - original_capacity
        print(f"Additional spots available with increased capacity: {additional_spots}")

if __name__ == "__main__":
    test_course_capacity()