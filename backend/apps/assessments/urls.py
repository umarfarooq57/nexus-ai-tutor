from django.urls import path
from . import views

app_name = 'assessments'

urlpatterns = [
    path('quiz/generate/', views.GenerateQuizView.as_view(), name='generate'),
    path('quiz/<uuid:pk>/', views.QuizDetailView.as_view(), name='quiz-detail'),
    path('quiz/submit/', views.SubmitQuizView.as_view(), name='submit'),
    path('quiz/results/<uuid:attempt_id>/', views.QuizResultsView.as_view(), name='results'),
    path('adaptive/', views.AdaptiveQuizView.as_view(), name='adaptive'),
]
