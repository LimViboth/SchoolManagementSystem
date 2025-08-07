from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from .models import Teacher
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from courses.models import CourseOffering, Enrollment
from django.contrib import messages
from django.urls import reverse
from django import forms
from django.db import models

class TeacherListView(LoginRequiredMixin, ListView):
    model = Teacher
    template_name = 'teachers/teacher_list.html'
    context_object_name = 'teachers'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_term = self.request.GET.get('search')
        if search_term:
            queryset = queryset.filter(
                Q(teacher_id__icontains=search_term) |
                Q(user__first_name__icontains=search_term) |
                Q(user__last_name__icontains=search_term)
            )
        return queryset

class TeacherDetailView(LoginRequiredMixin, DetailView):
    model = Teacher
    template_name = 'teachers/teacher_detail.html'
    context_object_name = 'teacher'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = self.get_object()
        from core.models import Semester
        current_semester = Semester.objects.filter(is_current=True).first()
        if current_semester:
            courses = teacher.teaching_courses.filter(semester=current_semester)
        else:
            courses = teacher.teaching_courses.all()
        context['courses'] = courses.select_related('course', 'semester')
        # Teaching history: group by semester and course, count students, average grade
        from courses.models import Enrollment
        teaching_history = []
        for offering in teacher.teaching_courses.select_related('course', 'semester').all():
            enrollments = Enrollment.objects.filter(course_offering=offering, withdrawn=False)
            total_students = enrollments.count()
            avg_grade = enrollments.exclude(grade__in=['W', 'I']).aggregate(avg=models.Avg('grade'))['avg']
            teaching_history.append({
                'term': str(offering.semester),
                'course': offering.course,
                'total_students': total_students,
                'average_grade': avg_grade or 0,
            })
        context['teaching_history'] = teaching_history
        return context

class GradeForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['grade', 'assignment_score', 'midterm_score', 'final_score']

@login_required
def manage_grades(request, offering_id):
    offering = get_object_or_404(CourseOffering, id=offering_id)
    teacher = offering.teacher
    if not (request.user.is_staff or (teacher and teacher.user == request.user)):
        messages.error(request, "You do not have permission to manage grades for this course.")
        return redirect('teachers:teacher_detail', pk=teacher.pk)

    enrollments = Enrollment.objects.filter(course_offering=offering, withdrawn=False).select_related('student__user')
    GradeFormSet = forms.modelformset_factory(Enrollment, form=GradeForm, extra=0)

    if request.method == 'POST':
        formset = GradeFormSet(request.POST, queryset=enrollments)
        if formset.is_valid():
            formset.save()
            messages.success(request, "Grades updated successfully.")
            return redirect(reverse('teachers:manage_grades', args=[offering_id]))
    else:
        formset = GradeFormSet(queryset=enrollments)

    return render(request, 'teachers/manage_grades.html', {
        'offering': offering,
        'formset': formset,
    })
