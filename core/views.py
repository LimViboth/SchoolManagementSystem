from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout
from django.shortcuts import render, redirect
from students.models import Student
from teachers.models import Teacher
from courses.models import Course
from core.models import Department
from django.contrib.auth.decorators import login_required

def home_view(request):
    context = {}
    if request.user.is_authenticated:
        user = request.user
        if user.is_superuser:
            # Admin sees system overview
            context['dashboard_type'] = 'admin'
            context['total_students'] = Student.objects.count()
            context['total_teachers'] = Teacher.objects.count()
            context['active_courses'] = Course.objects.filter(courseoffering__is_active=True).distinct().count()
            context['total_departments'] = Department.objects.count()
        elif hasattr(user, 'student'):
            # Students see their courses and grades
            context['dashboard_type'] = 'student'
            student = user.student
            context['student'] = student
            context['enrolled_courses'] = student.enrolled_courses.all()
        elif hasattr(user, 'teacher'):
            # Teachers see their courses and students
            context['dashboard_type'] = 'teacher'
            teacher = user.teacher
            context['teacher'] = teacher
            context['teaching_courses'] = teacher.teaching_courses.all()
    return render(request, 'index.html', context)

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        if user.is_superuser:
            context['dashboard_type'] = 'admin'
            context['total_students'] = Student.objects.count()
            context['total_teachers'] = Teacher.objects.count()
            context['active_courses'] = Course.objects.filter(courseoffering__is_active=True).distinct().count()
            context['total_departments'] = Department.objects.count()
        elif hasattr(user, 'student'):
            context['dashboard_type'] = 'student'
            student = user.student
            context['student'] = student
            context['enrolled_courses'] = student.enrolled_courses.all()
        elif hasattr(user, 'teacher'):
            context['dashboard_type'] = 'teacher'
            teacher = user.teacher
            context['teacher'] = teacher
            context['teaching_courses'] = teacher.teaching_courses.all()
            
        return context

@login_required
def logout_view(request):
    logout(request)
    return redirect('home')
