# health_ai/services/pdf_processor.py
import fitz  # PyMuPDF
import re

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    pages_text = []
    for i in range(len(doc)):
        page = doc.load_page(i)
        pages_text.append({
            "page_number": i + 1,
            "text": page.get_text()
        })
    return pages_text

def chunk_text(text, chunk_size=500, overlap=50):
    # Simple whitespace-based chunking for now
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

def process_pdf_report(report_obj):
    from ..models import ReportChunk
    pages = extract_text_from_pdf(report_obj.file.path)
    
    all_chunks = []
    for page in pages:
        chunks = chunk_text(page["text"])
        for chunk_text_content in chunks:
            chunk_obj = ReportChunk.objects.create(
                report=report_obj,
                chunk_text=chunk_text_content,
                page_number=page["page_number"]
            )
            all_chunks.append(chunk_obj)
            
    return all_chunks
