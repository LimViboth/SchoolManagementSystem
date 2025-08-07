from django.db import models
from core.models import Department, Semester
from teachers.models import Teacher
from students.models import Student


class Course(models.Model):
    code = models.CharField(max_length=10, unique=True, db_index=True)
    name = models.CharField(max_length=100, db_index=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, db_index=True)
    credits = models.IntegerField(db_index=True)
    description = models.CharField(max_length=1000)
    prerequisites = models.ManyToManyField('self', blank=True, symmetrical=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['name']),
            models.Index(fields=['department', 'credits']),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"

    def get_unique_instructors(self):
        # Return all teachers who teach this course, without duplicates
        return Teacher.objects.filter(teaching_courses__course=self).distinct()


# ... rest of your models unchanged ...

class CourseOffering(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, db_index=True)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, db_index=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, related_name='teaching_courses',
                                db_index=True)
    max_students = models.IntegerField()
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # New fields
    schedule = models.CharField(max_length=255, blank=True, null=True)
    material = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ['course', 'semester', 'teacher']
        indexes = [
            models.Index(fields=['semester', 'is_active']),
            models.Index(fields=['course', 'semester']),
        ]

    def __str__(self):
        return f"{self.course.code} - {self.semester}"

    def get_current_enrollment_count(self):
        return self.enrollment_set.filter(withdrawn=False).count()

    def get_available_slots(self):
        return self.get_effective_capacity() - self.get_current_enrollment_count()

    def get_effective_capacity(self):
        current_enrollment = self.get_current_enrollment_count()
        if current_enrollment >= 0.9 * self.max_students:
            return int(self.max_students * 1.2)
        return self.max_students

    def is_full(self):
        return self.get_current_enrollment_count() >= self.get_effective_capacity()


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

    student = models.ForeignKey(Student, on_delete=models.CASCADE, db_index=True)
    course_offering = models.ForeignKey(CourseOffering, on_delete=models.CASCADE, db_index=True)
    enrollment_date = models.DateField(auto_now_add=True)
    assignment_score = models.FloatField(null=True, blank=True)
    midterm_score = models.FloatField(null=True, blank=True)
    final_score = models.FloatField(null=True, blank=True)
    grade = models.CharField(max_length=1, choices=GRADE_CHOICES, blank=True, null=True, db_index=True)
    withdrawn = models.BooleanField(default=False, db_index=True)
    withdrawal_date = models.DateField(null=True, blank=True)

    def calculate_total_score(self):
        total = 0
        if self.assignment_score:
            total += self.assignment_score
        if self.midterm_score:
            total += self.midterm_score
        if self.final_score:
            total += self.final_score
        return total

    class Meta:
        unique_together = ['student', 'course_offering']
        indexes = [
            models.Index(fields=['student', 'withdrawn']),
            models.Index(fields=['course_offering', 'withdrawn']),
            models.Index(fields=['grade']),
        ]

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
