from django.urls import path
from . import views

app_name = 'blockchain'

urlpatterns = [
    path('credentials/', views.CredentialListView.as_view(), name='credentials'),
    path('credentials/<uuid:pk>/', views.CredentialDetailView.as_view(), name='credential-detail'),
    path('issue/', views.IssueCredentialView.as_view(), name='issue'),
    path('verify/<str:credential_hash>/', views.VerifyCredentialView.as_view(), name='verify'),
]
