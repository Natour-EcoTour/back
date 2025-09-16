"""
Views for managing point reviews in the Natour API.
"""
# pylint: disable=no-member
import logging
from django.db import models
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import permission_classes

from natour.api.pagination import CustomPagination
from natour.api.utils.logging_decorators import api_logger, log_validation_error
from natour.api.serializers.review import CreateReviewSerializer, ReviewSerializer
from natour.api.models import Point, PointReview
from natour.api.schemas.review_schemas import (
    add_review_schema,
    get_user_reviews_schema
)

from natour.api.utils.get_ip import get_client_ip

logger = logging.getLogger("django")


@add_review_schema
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@api_logger("review_creation")
def add_review(request, point_id):
    """
    Add a review for a specific point.
    """
    user = request.user
    ip = get_client_ip(request)

    point = get_object_or_404(Point, id=point_id)

    existing_review = point.reviews.filter(user=user).first()
    if existing_review:
        return Response(
            {"detail": "Você já avaliou este ponto."},
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer = CreateReviewSerializer(data=request.data)
    if serializer.is_valid():
        review = serializer.save(user=user, point=point)

        avg = point.reviews.aggregate(models.Avg('rating'))['rating__avg'] or 0
        point.avg_rating = round(avg)
        point.save(update_fields=['avg_rating'])

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@get_user_reviews_schema
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
@api_logger("user_reviews_retrieval")
def get_user_reviews(request):
    """
    Gets reviews created by users.
    """
    if 'page' not in request.query_params:
        return Response(
            {"detail": "Você deve fornecer o parâmetro de paginação ?page=N."},
            status=status.HTTP_400_BAD_REQUEST
        )

    reviews = PointReview.objects.select_related('user', 'point').all()

    paginator = CustomPagination()
    page = paginator.paginate_queryset(reviews, request)
    if page:
        serializer = ReviewSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    return Response(
        {"detail": "Nenhuma avaliação encontrada."},
        status=status.HTTP_404_NOT_FOUND
    )
