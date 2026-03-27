import json, os , re
from groq import Groq



def extract_json(content):
    try:
        match = re.search(r"\{[\s\S]*\}", content)
        if match:
            return json.loads(match.group(0))
        else:
            raise Exception("No valid JSON found")
    except Exception as e:
        print("JSON PARSE ERROR >>>", content)
        raise e

client = Groq(api_key=os.getenv("OPENAI_API_KEY"))

def generate_insight(question, result, start_date=None, end_date=None):

    if not result:
        return {
            "insight": "No data found for given query",
            "confidence": 0.5
        }
        
    import copy
    limited_result = copy.deepcopy(result[:5])
    
    data_context = {
        "total_rows_returned": len(result),
        "sample_data": limited_result
    }
    
    from datetime import datetime
    today_str = datetime.now().strftime("%Y-%m-%d")

    prompt = f"""
        You are an expert Data Analyst.

        User question:
        {question}

        Data result summary (Showing a maximum of 5 rows):
        {json.dumps(data_context)}

        System Context:
        Today is {today_str}.

        Rules:
        - Generate a one-sentence professional insight that answers the user's question based on the data.
        - Mention the total rows returned if relevant to the question.
        - Return ONLY valid JSON
        - Do not add any explanation or conversational text
        - JSON must start with {{ and end with }}
        - NEVER hallucinate or invent names, dates, or numbers. Explicitly use ONLY the exact data names provided in the JSON result.
        
        Format:
        {{
            "insight": "Your concise one sentence insight here.",
            "confidence": 0.95
        }}
     """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )

    content = response.choices[0].message.content.strip()
    content = content.replace("```json", "").replace("```", "").strip()

    try:
        return extract_json(content)
    except:
        return {
            "insight": "Could not generate insight",
            "confidence": 0.3
        }