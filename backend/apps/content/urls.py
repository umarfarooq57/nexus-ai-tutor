from django.urls import path
from . import views

app_name = 'content'

urlpatterns = [
    path('topic/<uuid:topic_id>/', views.TopicContentView.as_view(), name='topic-content'),
    path('next/', views.NextContentView.as_view(), name='next'),
    path('<uuid:pk>/complete/', views.MarkCompleteView.as_view(), name='complete'),
    path('upload/', views.UploadDocumentView.as_view(), name='upload'),
    path('process/image/', views.ProcessImageView.as_view(), name='process-image'),
    path('process/video/', views.ProcessVideoView.as_view(), name='process-video'),
]
