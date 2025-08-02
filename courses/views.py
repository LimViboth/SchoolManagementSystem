from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from .models import Course, CourseOffering

class CourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_term = self.request.GET.get('search')
        if search_term:
            queryset = queryset.filter(
                Q(code__icontains=search_term) |
                Q(name__icontains=search_term)
            )
        return queryset

class CourseDetailView(LoginRequiredMixin, DetailView):
    model = Course
    template_name = 'courses/course_detail.html'
    context_object_name = 'course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()
        context['offerings'] = course.courseoffering_set.all()
        return context

class CourseOfferingDetailView(LoginRequiredMixin, DetailView):
    model = CourseOffering
    template_name = 'courses/course_offering_detail.html'
    context_object_name = 'offering'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        offering = self.get_object()
        context['enrollments'] = offering.enrollment_set.all()
        context['assignments'] = offering.assignment_set.all()
        return context
