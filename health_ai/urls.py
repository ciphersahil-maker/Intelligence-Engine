# health_ai/urls.py
from django.urls import path
from .views import ReportUploadView, AIQueryView, ReportListView

urlpatterns = [
    path('upload-report/', ReportUploadView.as_view(), name='upload-report'),
    path('ai-query/', AIQueryView.as_view(), name='ai-query'),
    path('reports/', ReportListView.as_view(), name='reports'),
]
