from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('', views.StudentDashboardView.as_view(), name='dashboard'),
    path('list/', views.StudentListView.as_view(), name='student_list'),
    path('<int:pk>/', views.StudentDetailView.as_view(), name='student_detail'),
    path('courses/registration/', views.CourseRegistrationView.as_view(), name='course_registration'),
    path('courses/register/<int:offering_id>/', views.register_course, name='register_course'),
    path('courses/drop/<int:offering_id>/', views.drop_course, name='drop_course'),
    path('register/', views.student_registration, name='registration'),
    path('grade/<int:pk>/', views.StudentGradeDetailView.as_view(), name='grade_detail'),
]
