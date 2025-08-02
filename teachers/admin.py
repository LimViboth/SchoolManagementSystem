from django.contrib import admin
from .models import Teacher, TeacherAttendance

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('teacher_id', 'get_full_name', 'department', 'qualification', 'is_active')
    list_filter = ('department', 'is_active')
    search_fields = ('teacher_id', 'user__first_name', 'user__last_name')
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Name'

@admin.register(TeacherAttendance)
class TeacherAttendanceAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'date', 'is_present')
    list_filter = ('date', 'is_present')
    search_fields = ('teacher__teacher_id', 'teacher__user__first_name')
