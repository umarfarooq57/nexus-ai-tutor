from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('profile/', views.StudentProfileView.as_view(), name='profile'),
    path('progress/', views.StudentProgressView.as_view(), name='progress'),
    path('analytics/', views.LearningAnalyticsView.as_view(), name='analytics'),
    path('weaknesses/', views.WeaknessAnalysisView.as_view(), name='weaknesses'),
    path('sessions/', views.LearningSessionListView.as_view(), name='sessions'),
    path('sessions/<uuid:pk>/', views.LearningSessionDetailView.as_view(), name='session-detail'),
]
