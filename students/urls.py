from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('', views.StudentDashboardView.as_view(), name='dashboard'),
    path('list/', views.StudentListView.as_view(), name='student_list'),
    path('<int:pk>/', views.StudentDetailView.as_view(), name='student_detail'),
    path('courses/registration/', views.CourseRegistrationView.as_view(), name='course_registration'),
]
