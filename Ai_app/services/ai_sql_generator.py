from django import db
from openai import OpenAI
import os,re
from ..utils.schema_loader import load_schema
import requests 
from groq import Groq
from functools import lru_cache
from django.db import connection

client = Groq(api_key=os.getenv("OPENAI_API_KEY"))
@lru_cache(maxsize=1)
def get_schema():
    query = """
    SELECT column_name, data_type
    FROM information_schema.columns
    WHERE table_name = 'booking'
      AND table_schema = 'public'
    ORDER BY ordinal_position;
    """

    with connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()

    columns = [f"{row[0]} ({row[1]})" for row in result]

    return "Table: booking\nColumns:\n" + "\n".join(columns)

def enrich_question(question):
    q = question.lower()

    if "cancellation" in q:
        question += " (use job_status = 'cancelled', count rows as cancellations)"

    if "revenue" in q:
        question += " (use SUM(total_client_charge))"

    if "unique" in q or "how many" in q:
        question += " (list the entities and include their specific count as 'count')"

    if "duplicate" in q or "same" in q:
        question += " (group by client_name, booked_date, and booked_start_time, and filter for HAVING count > 1. Include all these columns in SELECT)"

    return question


def auto_fix_group_by(sql):
    sql_lower = sql.lower()

    if any(func in sql_lower for func in ["sum(", "count(", "avg("]) and "group by" not in sql_lower:

        match = re.search(r"select(.*?)from", sql, re.IGNORECASE | re.DOTALL)

        if match:
            cols = match.group(1)

            non_agg_cols = []

            for col in cols.split(","):
                col_clean = col.strip()

                # ❌ skip aggregates
                if any(func in col_clean.lower() for func in ["sum(", "count(", "avg("]):
                    continue

                # ❌ skip complex expressions
                if "(" in col_clean:
                    continue

                # remove alias
                col_clean = re.sub(r"\s+as\s+\w+", "", col_clean, flags=re.IGNORECASE)

                non_agg_cols.append(col_clean.strip())

            if non_agg_cols:
                group_by_clause = " GROUP BY " + ", ".join(non_agg_cols)

                if "order by" in sql_lower:
                    sql = re.sub(r"order by", group_by_clause + " ORDER BY", sql, flags=re.IGNORECASE)
                else:
                    sql += group_by_clause

    return sql



def generate_sql(question):

    print("question >>>>", question)

    from datetime import datetime
    today_str = datetime.now().strftime("%Y-%m-%d")

    schema = get_schema()
    prompt = f"""
        You are an expert PostgreSQL Data Analyst.

        Database Schema:
        {schema}

        User Objective: "{question}"
        (Today's Date: {today_str})

        Task: Generate a precise PostgreSQL SELECT query answering the user's objective using ONLY the provided schema.

        Guardrails:
        1. Zero Hallucination: Strictly use only existing tables, columns, and relationships from the schema. Never invent column names or hallucinate data. The table name is strictly 'booking'.
        2. Semantic Mapping: Intelligently map natural language to SQL (e.g., "cancelled" means `job_status = 'cancelled'`; use Today's Date to resolve relative date requests against `booked_date`).
        3. Aggregation & Structure: When calculating aggregate metrics (like COUNT) or asked for 'unique' or 'duplicate' lists, ALWAYS include the identifying columns (e.g., `client_name`, `booked_date`, `booked_start_time`) and the occurrence count (using `COUNT(*)`) in the SELECT clause and GROUP BY them. Aliases must be concise (e.g., `AS count`, `AS total`).
        4. Detail Inclusion: If the user asks about specific records or 'duplicates', ensure the response includes enough columns to identify the records (name, date, time).
        5. Safe Outputs: Always append `LIMIT 50` unless otherwise specified.
        5. Strict Format: Return ONLY valid, executable raw SQL code. Do NOT wrap in markdown, no explanations, no preamble.
    """
   
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0   # 🔥 VERY IMPORTANT (stability)
        )

        content = response.choices[0].message.content.strip()

        sql = content.replace("```sql", "").replace("```", "").strip()

        queries = re.findall(r"(SELECT[\s\S]*?;)", sql, re.IGNORECASE)

        queries = re.findall(r"(SELECT[\s\S]*?;)", sql, re.IGNORECASE)
        if queries:
            sql = queries[0]

        sql = re.sub(r"team_member_status\s*=\s*'[^']*'", "", sql, flags=re.IGNORECASE)
        sql = sql.replace("WHERE  AND", "WHERE")
        sql = auto_fix_group_by(sql)
        print("FINAL SQL >>>", sql)

        # 🔥 SAFETY CHECK
        if not sql.lower().startswith("select"):
            raise Exception("Invalid SQL generated")

        return sql

    except Exception as e:
        print("SQL GENERATION ERROR >>>", str(e))
        raise Exception(f"SQL Generation Failed: {str(e)}")

def generate_sql_with_retry(question, retries=3):
    for i in range(retries):
        try:
            sql = generate_sql(question)
            return sql
        except Exception as e:
            print(f"Retry {i+1} failed:", str(e))

    raise Exception("SQL Generation Failed after retries")





























 # schema = """
    #     Table: booking

    #     Columns:
    #     client_name
    #     team_member_name
    #     team_member_status
    #     country
    #     city
    #     job_status
    #     booked_date
    #     booked_end_date
    #     booked_start_time
    #     booked_end_time
    #     client_hourly_rate
    #     credit_card_fee
    #     rush_fee
    #     gratuity
    #     total_client_charge
    #     number_of_children
    #     category
    #     created_at
    # """
    #---------------------old prompt---------------------
    # prompt = f"""
    #     You are a PostgreSQL expert.

    #     Database Schema:
    #     {schema}

    #     User Question:
    #     {question}

      
    #     Rules:
    #     - Only SELECT queries
        
        
    #     - Do NOT assume values like 'completed'
    #     - Do NOT add random filters
    #     - Use aggregation when needed (COUNT, SUM, etc.)
    #     - Do NOT explain anything
    #     - Do NOT add markdown
    #     - Start query directly with SELECT
    #     - Limit results to 50

    #     - Use ONLY columns from schema
    #     - Do NOT invent column names
    #     - If question mentions "hours" or "duration", use:
    #         EXTRACT(EPOCH FROM (booked_end_time - booked_start_time))/3600
    #     - If booked_end_time is less than booked_start_time, treat it as next day (add 24 hours)
    #     - When using ORDER BY COUNT(*), include COUNT(*) in SELECT as total
    #     - If question mentions cancellations, use:
    #         job_status = 'cancelled'
    #     - Do NOT include functions or expressions in GROUP BY, only column names
        

    #     Return SQL only.
    # """

    #---------------------new prompt---------------------
    # prompt = f"""
    #     You are an expert PostgreSQL query generator.

    #     Database Schema:
    #     {schema}

    #     User Question:
    #     {question}

    #     Instructions:

    #     1. Generate a correct SQL query based ONLY on the schema.
    #     2. Understand the user intent (count, sum, duration, grouping, etc.)
    #     3. Use appropriate SQL functions when needed.

    #     Strict Rules:
    #     - Use ONLY columns from schema
    #     - Do NOT invent column names
    #     - Do NOT assume values unless specified
    #     - Only generate SELECT queries
    #     - Do NOT explain anything
    #     - Output ONLY SQL (no markdown)

    #     Smart Rules:
    #     - If aggregation is used (COUNT, SUM, AVG), include GROUP BY correctly
    #     - If ORDER BY COUNT(*), include COUNT(*) as alias "total"
    #     - If calculating duration:
    #     Use:
    #     CASE 
    #         WHEN booked_end_time < booked_start_time 
    #         THEN EXTRACT(EPOCH FROM (booked_end_time + INTERVAL '24 hours' - booked_start_time))/3600
    #         ELSE EXTRACT(EPOCH FROM (booked_end_time - booked_start_time))/3600
    #     END

    #     - If question mentions "cancellations":
    #     use job_status = 'cancelled'

    #     - Always add LIMIT 50

    #     Return SQL only.
    # """