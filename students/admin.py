from django.contrib import admin
from .models import Student, StudentAttendance

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'get_full_name', 'department', 'admission_year', 'is_active')
    list_filter = ('department', 'admission_year', 'is_active')
    search_fields = ('student_id', 'user__first_name', 'user__last_name')
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Name'

@admin.register(StudentAttendance)
class StudentAttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'is_present')
    list_filter = ('date', 'is_present')
    search_fields = ('student__student_id', 'student__user__first_name')
