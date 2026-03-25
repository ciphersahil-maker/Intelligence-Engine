from rest_framework.pagination import PageNumberPagination

class BookingPagination(PageNumberPagination):
    page_size = 2200
    page_size_query_param = "page_size"
    max_page_size = 100