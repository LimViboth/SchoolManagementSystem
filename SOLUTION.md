# Solution for Enrollment IntegrityError Issue

## Issue Description

The application was experiencing an `IntegrityError` when students attempted to re-register for a course they had previously withdrawn from:

```
IntegrityError: ORA-00001: unique constraint (VIBOOTH.COURSES_E_STUDENT_I_CF58BD69_U) violated on table VIBOOTH.COURSES_ENROLLMENT columns (STUDENT_ID, COURSE_OFFERING_ID)
```

This error occurred because the `Enrollment` model has a unique constraint on the combination of `student_id` and `course_offering_id` fields, as defined in the model's `Meta` class:

```python
class Meta:
    unique_together = ['student', 'course_offering']
```

Even when a student withdrew from a course (by setting the `withdrawn=True` flag), the enrollment record still existed in the database. When the student tried to re-register for the same course, the application attempted to create a new enrollment record with the same student and course offering IDs, which violated the unique constraint.

## Solution Implemented

The solution was to modify the `register_course` view function in `students/views.py` to:

1. Check if a withdrawn enrollment already exists for the student and course offering
2. If it exists, reactivate it instead of creating a new one
3. Add proper error handling for any database errors that might still occur

### Changes Made

The following changes were made to the `register_course` function:

```python
# Check if a withdrawn enrollment exists and reactivate it instead of creating a new one
existing_enrollment = Enrollment.objects.filter(
    student=student, 
    course_offering=course_offering, 
    withdrawn=True
).first()

if existing_enrollment:
    # Reactivate the enrollment
    existing_enrollment.withdrawn = False
    existing_enrollment.withdrawal_date = None
    existing_enrollment.enrollment_date = timezone.now().date()
    existing_enrollment.save()
    messages.success(request, f"Successfully re-registered for {course_offering.course.code}.")
    return HttpResponseRedirect(reverse('students:course_registration'))
```

Additionally, error handling was added around the enrollment creation:

```python
try:
    # Create enrollment
    Enrollment.objects.create(
        student=student,
        course_offering=course_offering
    )
    messages.success(request, f"Successfully registered for {course_offering.course.code}.")
except Exception as e:
    # Handle any database errors, including IntegrityError
    messages.error(request, f"Error registering for course: {str(e)}")
```

## Testing

A test script (`test_enrollment.py`) was created to verify the solution. The test confirmed that:

1. Creating a new enrollment works correctly
2. Attempting to create a duplicate enrollment raises an IntegrityError
3. Even withdrawn enrollments cause unique constraint violations

The test results confirmed that our approach of reactivating existing withdrawn enrollments instead of creating new ones is the correct solution.

## Conclusion

The issue was resolved by modifying the course registration process to handle withdrawn enrollments properly. Instead of attempting to create a new enrollment record (which would violate the unique constraint), the application now checks for existing withdrawn enrollments and reactivates them if found.

This solution maintains data integrity while allowing students to re-register for courses they had previously withdrawn from.