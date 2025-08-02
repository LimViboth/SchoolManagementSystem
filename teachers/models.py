from django.db import models
from django.contrib.auth.models import User
from core.models import Department

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    teacher_id = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    date_of_birth = models.DateField()
    address = models.CharField(max_length=500)
    phone = models.CharField(max_length=15)
    qualification = models.CharField(max_length=100)
    joining_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.teacher_id})"

class TeacherAttendance(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    date = models.DateField()
    is_present = models.BooleanField(default=False)
    note = models.CharField(max_length=500, blank=True)
    
    class Meta:
        unique_together = ['teacher', 'date']
    
    def __str__(self):
        return f"{self.teacher.user.get_full_name()} - {self.date}"
