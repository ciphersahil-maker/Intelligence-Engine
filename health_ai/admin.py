from django.contrib import admin
from .models import UploadedReport, ReportChunk, QueryLog

# Register your models here.
admin.site.register(UploadedReport)
admin.site.register(ReportChunk)
admin.site.register(QueryLog)   