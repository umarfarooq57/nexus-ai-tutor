from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('dashboard/', views.DashboardAnalyticsView.as_view(), name='dashboard'),
    path('metrics/', views.LearningMetricsView.as_view(), name='metrics'),
    path('topics/', views.TopicBreakdownView.as_view(), name='topics'),
    path('trends/', views.TrendsView.as_view(), name='trends'),
]
