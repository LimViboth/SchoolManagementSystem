from django.contrib import admin
from .models import Course, CourseOffering, Enrollment, Assignment, AssignmentSubmission

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'department', 'credits')
    list_filter = ('department', 'credits')
    search_fields = ('code', 'name')
    filter_horizontal = ('prerequisites',)

@admin.register(CourseOffering)
class CourseOfferingAdmin(admin.ModelAdmin):
    list_display = ('course', 'semester', 'teacher', 'max_students', 'is_active')
    list_filter = ('semester', 'is_active')
    search_fields = ('course__code', 'course__name', 'teacher__user__first_name')

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course_offering', 'enrollment_date', 'grade', 'withdrawn')
    list_filter = ('course_offering__semester', 'withdrawn', 'grade')
    search_fields = ('student__student_id', 'course_offering__course__code')

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course_offering', 'due_date', 'total_marks')
    list_filter = ('course_offering__semester', 'due_date')
    search_fields = ('title', 'course_offering__course__code')

@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'student', 'submission_date', 'marks_obtained')
    list_filter = ('submission_date',)
    search_fields = ('student__student_id', 'assignment__title')
