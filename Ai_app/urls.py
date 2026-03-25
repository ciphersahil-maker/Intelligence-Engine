from django.urls import path
from .views import *
urlpatterns = [
    path('bulk_upload/', BookingBulkCreate.as_view(), name='bulk_upload'),
    path('ai_analysis/', AIAnalysisAPIView.as_view(), name='ai_analysis'),
    path('create_booking/', CreateBookingAPIView.as_view(), name='create_booking'),
    path('run-sql/', RunSQLAPIView.as_view(), name='run-sql'),
]