"""
Module for handling pagination in API responses.
"""

from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """
    Custom pagination class to handle API responses.
    """
    page_size = 15
    page_size_query_param = 'page_size'
    max_page_size = 100
