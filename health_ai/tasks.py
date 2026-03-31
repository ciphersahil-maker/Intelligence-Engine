# health_ai/tasks.py
from celery import shared_task
from .models import UploadedReport
from .services.pdf_processor import process_pdf_report
from .services.gemini_service import get_embeddings
from .services.pinecone_service import upsert_chunks

@shared_task
def process_report_task(report_id, user_id):
    try:
        report = UploadedReport.objects.get(id=report_id)
        chunks = process_pdf_report(report)
        texts = [c.chunk_text for c in chunks]
        embeddings = get_embeddings(texts)
        upsert_chunks(user_id, chunks, embeddings)
        return f"Report {report_id} processed successfully"
    except Exception as e:
        return f"Error processing report {report_id}: {str(e)}"
