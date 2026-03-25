import openai
import json


# def generate_insight(question, result, start_date, end_date):

#     prompt = f"""
# You are a data analyst.

# User question:
# {question}

# Data result:
# {json.dumps(result)}

# Date range:
# {start_date} to {end_date}

# Explain the insight in one sentence.

# Also provide confidence score between 0 and 1.
# Return JSON format:
# {{
# "insight": "...",
# "confidence": 0.95
# }}
# """

#     response = openai.ChatCompletion.create(
#         model="gpt-4o",
#         messages=[{"role": "user", "content": prompt}]
#     )

#     content = response["choices"][0]["message"]["content"]

#     return json.loads(content)

# import requests
# import json , os
# from groq import Groq
# client = Groq(api_key=os.getenv("OPENAI_API_KEY"))

# def generate_insight(question, result, start_date, end_date):

#     prompt = f"""
#         You are a data analyst.

#         User question:
#         {question}

#         Data result:
#         {json.dumps(result)}

#         Date range:
#         {start_date} to {end_date}

#         Rules:
#         - Return ONLY valid JSON
#         - Do not add explanation
#         - Do not add text before or after JSON
#         - JSON must start with {{ and end with }}

#         Format:
#         {{
#         "insight": "one sentence insight",
#         "confidence": 0.95
#         }}
#     """

#     response = client.chat.completions.create(
#         model="llama-3.1-8b-instant",
#         messages=[
#             {"role": "user", "content": prompt}
#         ]
#     )

#     # ✅ Groq response handling
#     content = response.choices[0].message.content.strip()

#     print("GROQ RAW RESPONSE >>>", content)

#     print("MODEL CONTENT >>>", content)

#     # remove markdown if model adds it
#     content = content.replace("```json", "").replace("```", "").strip()

#     return json.loads(content)


# --------------------------old code-------------------------

import json
import os , re
from groq import Groq



def extract_json(content):
    try:
        # extract first JSON object
        match = re.search(r"\{[\s\S]*\}", content)
        if match:
            return json.loads(match.group(0))
        else:
            raise Exception("No valid JSON found")
    except Exception as e:
        print("JSON PARSE ERROR >>>", content)
        raise e

client = Groq(api_key=os.getenv("OPENAI_API_KEY"))

def generate_insight(question, result, start_date, end_date):

    if not result:
        return {
            "insight": "No data found for given query",
            "confidence": 0.5
        }

    prompt = f"""
         You are a data analyst.

         User question:
         {question}

         Data result:
         {json.dumps(result)}

         Date range:
         {start_date} to {end_date}

         Rules:
         - Return ONLY valid JSON
         - Do not add explanation
         - Do not add text before or after JSON
         - JSON must start with {{ and end with }}
         
         Format:
            {{
                "insight": "one sentence insight",
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