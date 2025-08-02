from django.db import models
from core.models import Department, Semester
from teachers.models import Teacher
from students.models import Student

class Course(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    credits = models.IntegerField()
    description = models.CharField(max_length=1000)
    prerequisites = models.ManyToManyField('self', blank=True, symmetrical=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

class CourseOffering(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)
    max_students = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['course', 'semester', 'teacher']

    def __str__(self):
        return f"{self.course.code} - {self.semester}"

class Enrollment(models.Model):
    GRADE_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('F', 'F'),
        ('W', 'Withdrawn'),
        ('I', 'Incomplete'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course_offering = models.ForeignKey(CourseOffering, on_delete=models.CASCADE)
    enrollment_date = models.DateField(auto_now_add=True)
    assignment_score = models.FloatField(null=True, blank=True)  # Out of 30
    midterm_score = models.FloatField(null=True, blank=True)    # Out of 30
    final_score = models.FloatField(null=True, blank=True)      # Out of 40
    grade = models.CharField(max_length=1, choices=GRADE_CHOICES, blank=True, null=True)
    withdrawn = models.BooleanField(default=False)
    withdrawal_date = models.DateField(null=True, blank=True)

    def calculate_total_score(self):
        total = 0
        if self.assignment_score:
            total += self.assignment_score  # 30% weight
        if self.midterm_score:
            total += self.midterm_score     # 30% weight
        if self.final_score:
            total += self.final_score       # 40% weight
        return total

    class Meta:
        unique_together = ['student', 'course_offering']

    def __str__(self):
        return f"{self.student.student_id} - {self.course_offering.course.code}"

class Assignment(models.Model):
    course_offering = models.ForeignKey(CourseOffering, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateTimeField()
    total_marks = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.course_offering.course.code}"

class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    submission_date = models.DateTimeField(auto_now_add=True)
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    feedback = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['assignment', 'student']

    def __str__(self):
        return f"{self.student.student_id} - {self.assignment.title}"
