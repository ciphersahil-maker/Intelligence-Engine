from django.shortcuts import render
from datetime import timedelta
from django.utils.timezone import now
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Record , Booking
from rest_framework.permissions import AllowAny
import pdfplumber , re

from .models import Booking
from .serializers import BookingSerializer
from .pagination import BookingPagination
# class Last7DaysInsights(APIView):

#     def get(self, request):

#         last_week = now() - timedelta(days=7)

#         data = Record.objects.filter(created_at__gte=last_week)

#         total = data.count()

#         avg = data.aggregate(avg_value=models.Avg("value"))

#         return Response({
#             "query": "last_7_days",
#             "total_records": total,
#             "average": avg
#         })
    

import random
from datetime import datetime, timedelta

def generate_dummy_bookings(count=1050):

    first_names = ["Ava","Liam","Noah","Emma","Olivia","Elijah","James","Sophia","Lucas","Mia","Ethan","Amelia"]
    last_names = ["Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis","Rodriguez","Martinez"]
    cities = ["Houston","Dallas","Austin","San Antonio","Manvel","Plano"]
    team_members = ["Alex Carter","Jordan Lee","Taylor Smith","Morgan Blake","Casey Jordan","Riley Quinn"]

    def random_date():
        start = datetime(2026,3,1)
        end = datetime(2026,3,31)
        delta = end - start
        return start + timedelta(days=random.randint(0, delta.days))

    def random_end_time(start_hour):
        duration = random.randint(8,12)
        end_hour = (start_hour + duration) % 24
        return f"{end_hour:02d}:00:00"

    data = []

    for _ in range(count):
        start_dt = random_date()
        start_hour = random.randint(17,23)

        record = {
            "Client Name": f"{random.choice(first_names)} {random.choice(last_names)}",
            "Team Member Name": random.choice(team_members),
            "Team Member Status": "Assigned",
            "Country": "",
            "City": random.choice(cities),
            "Locations": "[]",
            "Job Status": "Assigned",
            "Booked Date": start_dt.strftime("%Y-%m-%d"),
            "Booked End Date": (start_dt + timedelta(days=1)).strftime("%Y-%m-%d"),
            "Booked Start Time": f"{start_hour:02d}:00:00",
            "Booked End Time": random_end_time(start_hour),
            "Client Hourly Rate": random.choice([40.0,42.0,45.0,50.0]),
            "Credit Card Fee": 0.0,
            "Rush Fee": 0.0,
            "Gratuity": 0.0,
            "Total Client Charge": None,
            "Number of Children": random.randint(1,3),
            "Category": "Doula/NCS",
            "Notes": "",
            "Client Confirm Notes": None,
            "Ages of children": None,
            "Pet Selection": str([random.randint(100000,150000) for _ in range(random.randint(0,3))]),
            "Deposit Amount": None,
            "Booking fee": 0.0,
            "Is this a nanny trial?": ""
        }

        data.append(record)

    return data


    
class BookingBulkCreate(APIView):

    permission_classes = [AllowAny]

    def get(self, request):

        bookings = Booking.objects.all().order_by("-id")

        paginator = BookingPagination()
        result_page = paginator.paginate_queryset(bookings, request)

        serializer = BookingSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)
        

    def post(self, request):
        data = generate_dummy_bookings(1050)

        bookings = []

        for item in data:

            bookings.append(
                Booking(
                    client_name = item.get("Client Name"),
                    team_member_name = item.get("Team Member Name"),
                    team_member_status = item.get("Team Member Status"),
                    country = item.get("Country"),
                    city = item.get("City"),
                    locations = item.get("Locations"),
                    job_status = item.get("Job Status"),
                    booked_date = item.get("Booked Date"),
                    booked_end_date = item.get("Booked End Date"),
                    booked_start_time = item.get("Booked Start Time"),
                    client_hourly_rate = item.get("Client Hourly Rate"),
                    credit_card_fee = item.get("Credit Card Fee"),
                    rush_fee = item.get("Rush Fee"),
                    gratuity = item.get("Gratuity"),
                    total_client_charge = item.get("Total Client Charge"),
                    booked_end_time = item.get("Booked End Time"),
                    number_of_children = item.get("Number of Children"),
                    category = item.get("Category"),
                    notes = item.get("Notes"),
                    client_confirm_notes = item.get("Client Confirm Notes"),
                    ages_of_children = item.get("Ages of children"),
                    pet_selection = item.get("Pet Selection"),
                    deposit_amount = item.get("Deposit Amount"),
                    booking_fee = item.get("Booking fee"),
                    nanny_trial = item.get("Is this a nanny trial?")
                )
            )

        Booking.objects.bulk_create(bookings)

        return Response({
            "message": "Bookings uploaded successfully",
            "count": len(bookings)
        })
    

import traceback
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import JSONRenderer
# from .services.ai_sql_generator import generate_sql
# from .services.sql_validator import validate_sql
# from .services.query_runner import run_query
# from .services.insight_generator import generate_insight

from .services.ai_sql_generator import generate_sql_with_retry, get_schema
from .services.sql_validator import validate_sql, validate_columns
from .services.query_runner import run_query
from .services.insight_generator import generate_insight

import logging
logger = logging.getLogger(__name__)


class AIAnalysisAPIView(APIView):
    permission_classes = [AllowAny]
    renderer_classes = [JSONRenderer]

    def post(self, request):

        question = request.data.get("prompt")
        # validation
        if not question:
            return Response(
                {"error": "Question required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # # 1️⃣ Generate SQL
            # sql_query = generate_sql(question, start_date, end_date)

            # # 2️⃣ SQL Security Check
            # validate_sql(sql_query)

            # # 3️⃣ Run SQL Query
            # result = run_query(sql_query)

            # # 4️⃣ Generate Insight
            # insight_data = generate_insight(
            #     question,
            #     result,
            #     start_date,
            #     end_date
            # )..


            # 1️⃣ Generate SQL (with retry)
            sql_query = generate_sql_with_retry(question)

            # 2️⃣ Validate SQL
            validate_sql(sql_query)

            # 3️⃣ Validate columns
            schema = get_schema()
            validate_columns(sql_query, schema)

            # 4️⃣ Run Query
            try:
                result = run_query(sql_query)

            except Exception as e:

                error_msg = str(e)

                if "GROUP BY" in error_msg:
                    print("FIXING GROUP BY ERROR...")

                    from Ai_app.services.ai_sql_generator import auto_fix_group_by

                    sql_query = auto_fix_group_by(sql_query)

                    print("FIXED SQL >>>", sql_query)

                    result = run_query(sql_query)

                else:
                    raise e

            # 5️⃣ Insight
            print("Generating insight... ---------------------------------------->>>>",sql_query)
            insight_data = generate_insight(
                question,
                result,
                None,
                None
            )

            # Logging
            logger.info(f"Question: {question}")
            logger.info(f"SQL: {sql_query}")
            logger.info(f"Rows: {len(result)}")

            return Response({
                "question": question,
                "date_range": "Dynamically tracked by AI",
                "sql_query": sql_query,
                "data_points": len(result),
                "result": result,
                "insight": insight_data.get("insight"),
                "confidence": insight_data.get("confidence"),
            })

        except Exception as e:

            return Response(
                {
                    "error": str(e),
                    "trace": traceback.format_exc()
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CreateBookingAPIView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        data = request.data.copy()
        
        # provide defaults for missing required fields sent from frontend
        data.setdefault("team_member_status", "Pending")
        data.setdefault("job_status", "Upcoming")
        data.setdefault("booked_end_date", data.get("booked_date"))
        data.setdefault("client_hourly_rate", 0.0)
        data.setdefault("number_of_children", 1)
        
        serializer = BookingSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Booking created successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

import time
import decimal
from datetime import date, datetime
from django.db import connection
from rest_framework.permissions import IsAdminUser

class RunSQLAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        query = request.data.get("query", "").strip()
        if not query:
            return Response({"error": "Invalid SQL query. Query is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate query: Allow only SELECT
        query_upper = query.upper()
        if not query_upper.startswith("SELECT"):
            return Response({"error": "Invalid SQL query. Only SELECT queries are allowed."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Reject forbidden keywords
        forbidden_keywords = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE"]
        for keyword in forbidden_keywords:
            if keyword in query_upper:
                return Response({"error": f"Invalid SQL query. '{keyword}' is not allowed."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Apply max row limit if LIMIT not provided
        if "LIMIT" not in query_upper:
            query = query.rstrip(";") + " LIMIT 1000;"
            
        start_time = time.time()
        
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                columns = [col[0] for col in cursor.description] if cursor.description else []
                rows = cursor.fetchall()
        except Exception as e:
            return Response({"error": f"Invalid SQL query. {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
            
        execution_time = float(f"{time.time() - start_time:.4f}")
        
        # Convert SQL result into structured JSON
        result_data = []
        for row in rows:
            row_dict = {}
            for col_name, value in zip(columns, row):
                if isinstance(value, decimal.Decimal):
                    val = float(value)
                elif isinstance(value, (datetime, date)): # datetime is imported as class on line 33
                    val = value.isoformat()
                else:
                    val = value
                row_dict[col_name] = val
            result_data.append(row_dict)
            
        total_time = float(f"{time.time() - start_time:.4f}")
        
        return Response({
            "query_used": query,
            "execution_time": execution_time,
            "total_time": total_time,
            "timing_breakdown": {
                "query_execution_time": execution_time
            },
            "data": result_data,
            "meta": {
                "row_count": len(result_data),
                "columns": columns
            }
        }, status=status.HTTP_200_OK)
