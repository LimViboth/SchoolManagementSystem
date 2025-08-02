from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q, Avg, Count
from django.utils import timezone
from .models import Student
from django.contrib.auth.models import User
from courses.models import CourseOffering, Enrollment
from core.models import Department, Semester

class StudentListView(LoginRequiredMixin, ListView):
    model = Student
    template_name = 'students/student_list.html'
    context_object_name = 'students'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_term = self.request.GET.get('search')
        if search_term:
            queryset = queryset.filter(
                Q(student_id__icontains=search_term) |
                Q(user__first_name__icontains=search_term) |
                Q(user__last_name__icontains=search_term)
            )
        return queryset

class StudentDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'students/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = get_object_or_404(Student, user=self.request.user)
        current_semester = Semester.objects.filter(is_current=True).first()
        
        # Get current enrollments
        current_enrollments = Enrollment.objects.filter(
            student=student,
            course_offering__semester=current_semester,
            withdrawn=False
        )

        # Calculate attendance percentage
        attendance_count = student.studentattendance_set.count()
        if attendance_count > 0:
            present_count = student.studentattendance_set.filter(is_present=True).count()
            attendance_percentage = (present_count / attendance_count) * 100
        else:
            attendance_percentage = 0

        # Calculate GPA
        enrolled_courses = Enrollment.objects.filter(
            student=student,
            grade__isnull=False
        ).exclude(grade__in=['W', 'I'])
        
        if enrolled_courses.exists():
            grade_points = {
                'A': 4.0, 'B': 3.0, 'C': 2.0, 'D': 1.0, 'F': 0.0
            }
            total_points = sum(grade_points.get(enrollment.grade, 0) * enrollment.course_offering.course.credits 
                             for enrollment in enrolled_courses)
            total_credits = sum(enrollment.course_offering.course.credits for enrollment in enrolled_courses)
            gpa = total_points / total_credits if total_credits > 0 else 0
        else:
            gpa = 0

        context.update({
            'student': student,
            'current_courses_count': current_enrollments.count(),
            'attendance_percentage': round(attendance_percentage, 1),
            'gpa': round(gpa, 2),
            'current_enrollments': current_enrollments,
            'recent_assignments': student.assignmentsubmission_set.all()[:5]
        })
        return context

class StudentDetailView(LoginRequiredMixin, DetailView):
    model = Student
    template_name = 'students/student_detail.html'
    context_object_name = 'student'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.get_object()
        current_semester = Semester.objects.filter(is_current=True).first()

        # Get current enrollments and grades
        current_grades = student.enrollment_set.filter(
            course_offering__semester=current_semester,
            withdrawn=False
        ).select_related('course_offering__course')

        # Calculate attendance statistics
        attendance_stats = student.studentattendance_set.filter(
            date__gte=timezone.now() - timezone.timedelta(days=90)  # Last 90 days
        ).aggregate(
            present_count=Count('id', filter=Q(is_present=True)),
            absent_count=Count('id', filter=Q(is_present=False))
        )
        
        # Get attendance logs
        attendance_logs = student.studentattendance_set.all().order_by('-date')[:30]  # Last 30 records
        
        # Calculate attendance rate per course
        attendance_summary = []
        for enrollment in current_grades:
            course_attendance = student.studentattendance_set.filter(
                course_offering=enrollment.course_offering
            ).aggregate(
                total=Count('id'),
                present=Count('id', filter=Q(is_present=True))
            )
            
            if course_attendance['total'] > 0:
                rate = (course_attendance['present'] / course_attendance['total']) * 100
            else:
                rate = 0
                
            attendance_summary.append({
                'course': enrollment.course_offering.course,
                'rate': rate
            })
        
        # Prepare attendance chart data
        attendance_chart_data = [
            attendance_stats.get('present_count', 0),
            attendance_stats.get('absent_count', 0),
            0  # We don't have 'late' status in current model
        ]
        
        # Get grade history
        grade_history = student.enrollment_set.filter(
            withdrawn=False,
            grade__isnull=False
        ).exclude(
            grade__in=['W', 'I']
        ).order_by(
            'course_offering__semester__start_date'
        ).select_related(
            'course_offering__course',
            'course_offering__semester'
        )
        
        # Prepare grade history chart data
        semesters = Semester.objects.all().order_by('-start_date')
        grade_history_data = []
        grade_history_labels = []
        
        grade_points = {'A': 4.0, 'B': 3.0, 'C': 2.0, 'D': 1.0, 'F': 0.0}
        
        for semester in semesters:
            semester_enrollments = grade_history.filter(course_offering__semester=semester)
            if semester_enrollments.exists():
                semester_points = sum(
                    grade_points.get(enrollment.grade, 0) * enrollment.course_offering.course.credits 
                    for enrollment in semester_enrollments
                )
                semester_credits = sum(
                    enrollment.course_offering.course.credits 
                    for enrollment in semester_enrollments
                )
                semester_gpa = semester_points / semester_credits if semester_credits > 0 else 0
                
                grade_history_labels.append(str(semester))
                grade_history_data.append(round(semester_gpa, 2))
        
        context.update({
            'current_grades': current_grades,
            'grade_history': grade_history,
            'semesters': semesters,
            'attendance_summary': attendance_summary,
            'attendance_logs': attendance_logs,
            'attendance_stats': attendance_chart_data,
            'grade_history_labels': grade_history_labels,
            'grade_history_data': grade_history_data,
        })
        return context

class CourseRegistrationView(LoginRequiredMixin, TemplateView):
    template_name = 'students/course_registration.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = get_object_or_404(Student, user=self.request.user)
        current_semester = Semester.objects.filter(is_current=True).first()
        
        # Get available course offerings
        course_offerings = CourseOffering.objects.filter(
            semester=current_semester,
            is_active=True
        )

        # Apply filters
        search = self.request.GET.get('search')
        department = self.request.GET.get('department')
        credits = self.request.GET.get('credits')

        if search:
            course_offerings = course_offerings.filter(
                Q(course__code__icontains=search) |
                Q(course__name__icontains=search)
            )
        
        if department:
            course_offerings = course_offerings.filter(course__department_id=department)
        
        if credits:
            course_offerings = course_offerings.filter(course__credits=credits)

        # Add registration status and available slots
        for offering in course_offerings:
            offering.is_registered = Enrollment.objects.filter(
                student=student,
                course_offering=offering,
                withdrawn=False
            ).exists()
            
            enrolled_count = Enrollment.objects.filter(
                course_offering=offering,
                withdrawn=False
            ).count()
            
            offering.available_slots = offering.max_students - enrolled_count
            offering.is_full = offering.available_slots <= 0

        context.update({
            'current_semester': current_semester,
            'course_offerings': course_offerings,
            'departments': Department.objects.all()
        })
        return context
