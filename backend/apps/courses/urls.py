from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.CourseListView.as_view(), name='list'),
    path('<uuid:pk>/', views.CourseDetailView.as_view(), name='detail'),
    path('<uuid:course_id>/modules/', views.ModuleListView.as_view(), name='modules'),
    path('<uuid:course_id>/enroll/', views.EnrollView.as_view(), name='enroll'),
    path('enrollments/', views.EnrollmentListView.as_view(), name='enrollments'),
    path('topics/<uuid:pk>/', views.TopicDetailView.as_view(), name='topic-detail'),
]
