# health_ai/models.py
from django.db import models
from django.contrib.auth.models import User

class UploadedReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='reports/%Y/%m/%d/')
    report_type = models.CharField(max_length=100)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.report_type} ({self.uploaded_at})"

class ReportChunk(models.Model):
    report = models.ForeignKey(UploadedReport, on_delete=models.CASCADE, related_name='chunks')
    chunk_text = models.TextField()
    pinecone_id = models.CharField(max_length=255)
    page_number = models.IntegerField()

    def __str__(self):
        return f"Chunk {self.id} for {self.report.id} Page {self.page_number}"

class QueryLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.question[:50]}..."
