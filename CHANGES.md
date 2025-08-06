# Changes Log

## 2025-08-05: Fixed AttributeError in home_view

### Issue
The application was throwing an AttributeError when accessing the home page:
```
'Teacher' object has no attribute 'teaching_courses'
```

This error occurred in the `home_view` function in `core/views.py` at line 33, where it was trying to access `teacher.teaching_courses.all()`.

### Solution
Added a `related_name` parameter to the `teacher` field in the `CourseOffering` model:

```python
teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, related_name='teaching_courses', db_index=True)
```

This creates a reverse relationship that allows accessing course offerings from a teacher instance via the `teaching_courses` attribute.

### Implementation Details
1. Modified the `CourseOffering` model in `courses/models.py` to add the `related_name` parameter
2. Created a migration for the change: `courses/migrations/0005_alter_courseoffering_teacher.py`
3. Applied the migration using the `--fake` flag due to database conflicts
4. Verified the fix by testing the `Teacher` model and the `home_view` function

### Testing
- Confirmed that `Teacher` objects now have a `teaching_courses` attribute
- Verified that the `home_view` function works correctly with teacher users