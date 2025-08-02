from django.db import models
from django.contrib.auth.models import User
from core.models import Department, AcademicYear

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    date_of_birth = models.DateField()
    address = models.CharField(max_length=500)
    phone = models.CharField(max_length=15)
    admission_year = models.ForeignKey(AcademicYear, on_delete=models.SET_NULL, null=True)
    graduation_year = models.ForeignKey(AcademicYear, on_delete=models.SET_NULL, null=True, related_name='graduating_students')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.student_id})"

class StudentAttendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    is_present = models.BooleanField(default=False)
    note = models.CharField(max_length=500, blank=True)
    
    class Meta:
        unique_together = ['student', 'date']
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.date}"
