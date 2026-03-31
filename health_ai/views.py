# health_ai/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated,AllowAny
from .models import UploadedReport, QueryLog, ReportChunk
from .serializers import UploadedReportSerializer, QueryLogSerializer
from .services.pdf_processor import process_pdf_report
from .services.gemini_service import get_embeddings, get_question_embedding, generate_medical_answer
from .services.pinecone_service import upsert_chunks, query_pinecone

from django.contrib.auth import get_user_model

User = get_user_model()


class ReportUploadView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        file = request.FILES.get('file')
        report_type = request.data.get('report_type', 'General')

        if not file:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ FIX: assign admin if anonymous
        if request.user.is_authenticated:
            user = request.user
        else:
            user = User.objects.filter(is_superuser=True).first()  # admin user

            if not user:
                return Response(
                    {"error": "No admin user found"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        report = UploadedReport.objects.create(
            user=user,
            file=file,
            report_type=report_type
        )

        try:
            chunks = process_pdf_report(report)
            texts = [c.chunk_text for c in chunks]
            embeddings = get_embeddings(texts)

            # ✅ use correct user id
            upsert_chunks(user.id, chunks, embeddings)

            return Response({
                "message": "Report uploaded and processed successfully",
                "report_id": report.id
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                "error": f"Processing failed: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AIQueryView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        question = request.data.get('question')
        name = request.data.get('name')
        age = request.data.get('age')
        
        if not question:
            return Response({"error": "No question provided"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            # 1. Get embedding
            q_emb = get_question_embedding(question)
            
            # 2. Query Pinecone
            if request.user.is_authenticated:
                user_obj = request.user
            else:
                user_obj = User.objects.filter(is_superuser=True).first()
                if not user_obj:
                    return Response({"error": "No admin user found for context lookup"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            matches = query_pinecone(user_obj.id, q_emb, top_k=10)
            
            # 3. Prepare context with categories
            context_chunks = []
            for m in matches:
                chunk_info = f"[Category: {m.metadata.get('report_type', 'General')}] {m.metadata['chunk_text']}"
                context_chunks.append(chunk_info)
            
            # 4. Generate answer
            answer = generate_medical_answer(question, context_chunks, name=name, age=age)
            
            # 5. Log query (using fallback user if anonymous)
            QueryLog.objects.create(user=user_obj, question=question, answer=answer)
            
            return Response({
                "question": question,
                "answer": answer,
                "sources": [{"file": m.metadata['report_id'], "page": m.metadata['page_number'], "type": m.metadata.get('report_type')} for m in matches],
                "confidence": "high"
            })
        except Exception as e:
            return Response({"error": f"Query failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ReportListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        if request.user.is_authenticated:
            user = request.user
        else:
            user = User.objects.filter(is_superuser=True).first()

        if not user:
            return Response([])

        reports = UploadedReport.objects.filter(user=user).order_by('-uploaded_at')
        serializer = UploadedReportSerializer(reports, many=True)
        return Response(serializer.data)
