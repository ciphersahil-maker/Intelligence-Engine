import os
import django
from django.conf import settings

# Setup Django environment
if not settings.configured:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Ai_project.settings")
    django.setup()

from Ai_app.services.ai_sql_generator import generate_sql_with_retry, enrich_question

questions = [
    "how many unique client we have",
    "show me unique clients by date",
    "how many bookings per client",
    "Detect duplicate bookings (same client, same date, same time)"
]

with open("sql_gen_results.txt", "w") as f:
    for q in questions:
        f.write("-" * 50 + "\n")
        f.write(f"Question: {q}\n")
        enriched = enrich_question(q)
        f.write(f"Enriched: {enriched}\n")
        try:
            sql = generate_sql_with_retry(enriched)
            f.write("Generated SQL:\n")
            f.write(sql + "\n")
        except Exception as e:
            f.write(f"Error: {e}\n")
print("Results saved to sql_gen_results.txt")
