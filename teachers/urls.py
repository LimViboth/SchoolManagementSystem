from django.urls import path
from . import views

app_name = 'teachers'

urlpatterns = [
    path('', views.TeacherListView.as_view(), name='teacher_list'),
    path('<int:pk>/', views.TeacherDetailView.as_view(), name='teacher_detail'),
]
