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

from natour.api.utils.get_ip import get_client_ip

logger = logging.getLogger("django")


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_review(request, point_id):
    """
    Add a review for a specific point.
    """
    user = request.user
    ip = get_client_ip(request)
    logger.info(
        "User '%s' (ID: %s, IP: %s) requested to add a review to Point ID: %s.",
        user.username, user.id, ip, point_id
    )

    point = get_object_or_404(Point, id=point_id)

    existing_review = point.reviews.filter(user=user).first()
    if existing_review:
        logger.warning(
            "User '%s' (ID: %s) attempted to add a duplicate review for Point ID: %s (Review ID: %s).",
            user.username, user.id, point_id, existing_review.id
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
            "User '%s' (ID: %s) added Review ID: %s (Rating: %s) to Point ID: %s. New avg rating: %.2f",
            user.username, user.id, review.id, review.rating, point_id, avg
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    logger.warning(
        "User '%s' (ID: %s) failed to add review to Point ID: %s due to validation errors: %s",
        user.username, user.id, point_id, serializer.errors
    )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
