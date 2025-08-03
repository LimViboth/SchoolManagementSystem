# Course Capacity Enhancement

## Issue
The original system had a strict limit on course enrollment based on the `max_students` field in the `CourseOffering` model. When a course reached its maximum capacity, no more students could enroll, leading to limited available spots.

## Changes Made

### 1. Modified `register_course` View
Updated the course registration logic in `students/views.py` to increase the maximum capacity by 20%:

```python
# Increased capacity by 20% to allow more available spots
increased_capacity = int(course_offering.max_students * 1.2)
if enrolled_count >= increased_capacity:
    messages.error(request, f"Course {course_offering.course.code} is full.")
    return HttpResponseRedirect(reverse('students:course_registration'))
```

### 2. Updated `CourseRegistrationView`
Modified the view to calculate and display the increased capacity:

```python
# Increased capacity by 20% to allow more available spots
increased_capacity = int(offering.max_students * 1.2)
offering.available_slots = increased_capacity - enrolled_count
offering.is_full = offering.available_slots <= 0
offering.increased_max = increased_capacity
```

### 3. Updated Course Registration Template
Updated the template to display the increased capacity to students:

```html
{{ offering.available_slots }} / {{ offering.increased_max }}
<small class="text-muted d-block">(Extended capacity)</small>
```

## Impact

The changes have successfully increased the available spots for course enrollment by 20% across all courses. This means:

1. Courses that were previously full now have additional spots available
2. Students have more opportunities to enroll in their desired courses
3. The system can accommodate more students without requiring database changes to the actual `max_students` values

### Example Impact
For a course with a maximum capacity of 40 students:
- Original capacity: 40 students
- Increased capacity: 48 students (20% increase)
- Additional spots: 8 students

This enhancement provides flexibility in course enrollment while maintaining the original capacity values in the database.