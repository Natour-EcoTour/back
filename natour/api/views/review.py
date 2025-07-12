"""
Views for managing point reviews in the Natour API.
"""
# pylint: disable=no-member
import logging
from django.db import models
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import permission_classes

from natour.api.serializers.review import CreateReviewSerializer
from natour.api.models import Point

logger = logging.getLogger("django")


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_review(request, point_id):
    """
    Add a review for a specific point.
    """
    user = request.user
    logger.info(
        "Received request to add a review.",
    )

    point = get_object_or_404(Point, id=point_id)

    existing_review = point.reviews.filter(user=user).first()
    if existing_review:
        logger.warning(
            "User already reviewed this point.",
        )
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

        logger.info(
            "Review added successfully.",
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    logger.warning(
        "Failed to add review due to validation errors.",
    )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
