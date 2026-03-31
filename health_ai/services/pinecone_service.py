# health_ai/services/pinecone_service.py
import os
from pinecone import Pinecone, ServerlessSpec
from django.conf import settings

def get_pinecone_index():
    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        return None
        
    pc = Pinecone(api_key=api_key)
    index_name = "health-reports-v2"

    # Ensure index exists (Lazy check)
    try:
        if index_name not in [idx.name for idx in pc.list_indexes()]:
            pc.create_index(
                name=index_name,
                dimension=384, 
                metric='cosine',
                spec=ServerlessSpec(cloud='aws', region='us-east-1')
            )
        return pc.Index(index_name)
    except:
        return None

def upsert_chunks(user_id, chunks, embeddings):
    idx = get_pinecone_index()
    if not idx:
        print("Pinecone not configured")
        return
        
    vectors = []
    for chunk, emb in zip(chunks, embeddings):
        vectors.append({
            "id": str(chunk.id),
            "values": emb,
            "metadata": {
                "user_id": str(user_id),
                "report_id": str(chunk.report.id),
                "report_type": str(chunk.report.report_type),
                "page_number": chunk.page_number,
                "chunk_text": chunk.chunk_text
            }
        })
    
    idx.upsert(vectors=vectors, namespace=str(user_id))
    
    # Update local pinecone_id
    for chunk, vec in zip(chunks, vectors):
        chunk.pinecone_id = vec["id"]
        chunk.save()

def query_pinecone(user_id, question_embedding, top_k=5):
    idx = get_pinecone_index()
    if not idx:
        return []
        
    results = idx.query(
        namespace=str(user_id),
        vector=question_embedding,
        top_k=top_k,
        include_metadata=True
    )
    return results.matches
