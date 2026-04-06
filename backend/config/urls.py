"""
NEXUS AI Tutor - URL Configuration
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API v1
    path('api/v1/', include('api.v1.urls')),
    
    # App-specific URLs
    path('api/v1/auth/', include('apps.users.urls')),
    path('api/v1/students/', include('apps.students.urls')),
    path('api/v1/digital-twin/', include('apps.digital_twin.urls')),
    path('api/v1/courses/', include('apps.courses.urls')),
    path('api/v1/assessments/', include('apps.assessments.urls')),
    path('api/v1/analytics/', include('apps.analytics.urls')),
    path('api/v1/content/', include('apps.content.urls')),
    path('api/v1/reports/', include('apps.reports.urls')),
    path('api/v1/blockchain/', include('apps.blockchain.urls')),
    
    # Gemini AI Chat
    path('api/v1/agent/chat/', __import__('api.v1.gemini_views', fromlist=['GeminiChatView']).GeminiChatView.as_view(), name='gemini-chat'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug toolbar
    import debug_toolbar
    urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns
