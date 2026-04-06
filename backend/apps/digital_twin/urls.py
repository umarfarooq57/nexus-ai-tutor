from django.urls import path
from . import views

app_name = 'digital_twin'

urlpatterns = [
    path('state/', views.DigitalTwinStateView.as_view(), name='state'),
    path('predictions/', views.PredictionsView.as_view(), name='predictions'),
    path('events/', views.CognitiveEventsView.as_view(), name='events'),
    path('sync/', views.SyncDigitalTwinView.as_view(), name='sync'),
    path('knowledge-graph/', views.KnowledgeGraphView.as_view(), name='knowledge-graph'),
]
