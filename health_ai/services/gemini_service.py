# health_ai/services/gemini_service.py
import os
from groq import Groq
from sentence_transformers import SentenceTransformer

# Initialize Local Embedding Model (Runs on CPU/GPU)
# all-MiniLM-L6-v2 is fast and has 384 dimensions
embed_model = SentenceTransformer('all-MiniLM-L6-v2')
groq_client = Groq(api_key=os.getenv("OPENAI_API_KEY"))

def get_embeddings(texts):
    if isinstance(texts, str):
        texts = [texts]
    
    # Generate embeddings locally
    embeddings = embed_model.encode(texts)
    return [emb.tolist() for emb in embeddings]

def get_question_embedding(question):
    # Generate single embedding locally
    embedding = embed_model.encode([question])[0]
    return embedding.tolist()

def generate_medical_answer(question, context_chunks, name=None, age=None):
    context_text = "\n\n".join(context_chunks)
    
    user_context = f"Patient Name: {name}, Age: {age}" if name and age else ""
    
    prompt = f"""
    You are a highly skilled Medical Intelligence Assistant. {user_context}
    
    ### MISSION
    Analyze the provided medical context and provide a structured, professional response to the user's question. 
    
    ### CONTEXT GUIDELINES
    - ONLY use the provided context below.
    - If the context mentions specific lab values (e.g., "WBC: 11.5", "Hb: 14"), you MUST cite them exactly.
    - Do NOT hallucinate or guess any medical data.
    - If information is missing, clearly state that it is not available in the current reports.
    - Pay attention to the [Category: ...] tags to understand the source of each piece of information.

    ### RESPONSE STRUCTURE
    1. **Personalized Analysis**: Address the user (use name if provided). Summarize the key findings related to their question.
    2. **Evidence-Based Indicators (Pros & Cons)**: 
        - **Normal/Stable**: List findings that are within reference ranges.
        - **Abnormal/Concerning**: List findings that are flagged as high/low or outside ranges. Cite the specific values and the report category.
    3. **Recovery & Guidance**: Provide actionable steps based on the findings (e.g., "Based on your high glucose, avoid...") and always emphasize consulting their doctor for a clinical diagnosis.

    ### FORMATTING
    Use professional, empathetic language. Keep it concise but data-rich.

    Context:
    {context_text}

    Question:
    {question}
    """
    
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1 # Low temperature for high factual accuracy
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating answer: {str(e)}"
