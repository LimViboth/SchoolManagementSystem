from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q, Avg, Count
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect
from .models import Student
from django.contrib.auth.models import User
from courses.models import CourseOffering, Enrollment
from core.models import Department, Semester, AcademicYear
from django import forms

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

        # Get all enrolled courses
        all_enrolled_courses = student.enrolled_courses.all().select_related('course', 'semester', 'teacher')
        
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
            'all_enrolled_courses': all_enrolled_courses,
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
            
            # Use the model methods to get capacity information
            offering.available_slots = offering.get_available_slots()
            offering.is_full = offering.is_full()
            offering.increased_max = offering.get_effective_capacity()

        context.update({
            'current_semester': current_semester,
            'course_offerings': course_offerings,
            'departments': Department.objects.all()
        })
        return context


@login_required
@csrf_protect
def register_course(request, offering_id):
    """
    View function to register a student for a course offering
    """
    if request.method == 'POST':
        student = get_object_or_404(Student, user=request.user)
        course_offering = get_object_or_404(CourseOffering, id=offering_id)
        
        # Check if already registered (active enrollment)
        if Enrollment.objects.filter(student=student, course_offering=course_offering, withdrawn=False).exists():
            messages.warning(request, f"You are already registered for {course_offering.course.code}.")
            return HttpResponseRedirect(reverse('students:course_registration'))
        
        # Check if a withdrawn enrollment exists and reactivate it instead of creating a new one
        existing_enrollment = Enrollment.objects.filter(
            student=student, 
            course_offering=course_offering, 
            withdrawn=True
        ).first()
        
        if existing_enrollment:
            # Reactivate the enrollment
            existing_enrollment.withdrawn = False
            existing_enrollment.withdrawal_date = None
            existing_enrollment.enrollment_date = timezone.now().date()
            existing_enrollment.save()
            messages.success(request, f"Successfully re-registered for {course_offering.course.code}.")
            return HttpResponseRedirect(reverse('students:course_registration'))
        
        # Check if course is full using the model method
        if course_offering.is_full():
            messages.error(request, f"Course {course_offering.course.code} is full.")
            return HttpResponseRedirect(reverse('students:course_registration'))
        
        try:
            # Create enrollment
            Enrollment.objects.create(
                student=student,
                course_offering=course_offering
            )
            messages.success(request, f"Successfully registered for {course_offering.course.code}.")
        except Exception as e:
            # Handle any database errors, including IntegrityError
            messages.error(request, f"Error registering for course: {str(e)}")
        
    return HttpResponseRedirect(reverse('students:course_registration'))


@login_required
@csrf_protect
def drop_course(request, offering_id):
    """
    View function to drop a course enrollment
    """
    if request.method == 'POST':
        student = get_object_or_404(Student, user=request.user)
        course_offering = get_object_or_404(CourseOffering, id=offering_id)
        
        # Find the enrollment
        try:
            enrollment = Enrollment.objects.get(
                student=student,
                course_offering=course_offering,
                withdrawn=False
            )
            
            # Mark as withdrawn
            enrollment.withdrawn = True
            enrollment.withdrawal_date = timezone.now().date()
            enrollment.save()
            
            messages.success(request, f"Successfully dropped {course_offering.course.code}.")
        except Enrollment.DoesNotExist:
            messages.warning(request, f"You are not registered for {course_offering.course.code}.")
    
    return HttpResponseRedirect(reverse('students:course_registration'))


class StudentRegistrationForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput(), required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput(), required=True)
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    student_id = forms.CharField(max_length=20, required=True)
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=True)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    address = forms.CharField(max_length=500, required=True)
    phone = forms.CharField(max_length=15, required=True)
    admission_year = forms.ModelChoiceField(queryset=AcademicYear.objects.all(), required=True)
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords don't match")
        
        username = cleaned_data.get('username')
        if username and User.objects.filter(username=username).exists():
            self.add_error('username', "Username already exists")
            
        student_id = cleaned_data.get('student_id')
        if student_id and Student.objects.filter(student_id=student_id).exists():
            self.add_error('student_id', "Student ID already exists")
            
        email = cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            self.add_error('email', "Email already exists")
            
        return cleaned_data


@csrf_protect
def student_registration(request):
    """
    View function to register a new student
    """
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            # Create User
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
                email=form.cleaned_data['email'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name']
            )
            
            # Create Student
            student = Student.objects.create(
                user=user,
                student_id=form.cleaned_data['student_id'],
                department=form.cleaned_data['department'],
                date_of_birth=form.cleaned_data['date_of_birth'],
                address=form.cleaned_data['address'],
                phone=form.cleaned_data['phone'],
                admission_year=form.cleaned_data['admission_year'],
                graduation_year=None  # This can be set later
            )
            
            messages.success(request, "Registration successful! You can now log in.")
            return redirect('login')
    else:
        form = StudentRegistrationForm()
    
    return render(request, 'students/registration.html', {'form': form})
