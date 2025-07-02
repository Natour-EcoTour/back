"""
Views for managing point reviews in the Natour API.
"""
# pylint: disable=no-member

from django.db import models
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import permission_classes

from natour.api.serializers.review import CreateReviewSerializer
from natour.api.models import Point


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_review(request, point_id):
    """
    Add a review for a specific point.
    """
    point = get_object_or_404(Point, id=point_id)

    serializer = CreateReviewSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user, point=point)

        avg = point.reviews.aggregate(models.Avg('rating'))['rating__avg'] or 0
        point.avg_rating = round(avg)
        point.save(update_fields=['avg_rating'])
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
