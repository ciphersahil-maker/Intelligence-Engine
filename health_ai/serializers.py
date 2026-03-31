# health_ai/serializers.py
from rest_framework import serializers
from .models import UploadedReport, QueryLog

class UploadedReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedReport
        fields = ['id', 'file', 'report_type', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']

class QueryLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = QueryLog
        fields = ['id', 'question', 'answer', 'created_at']
        read_only_fields = ['id', 'answer', 'created_at']
