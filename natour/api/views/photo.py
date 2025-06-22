"""
Views for handling photo uploads in the Natour API.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
# from natour.api.models import Photo
from natour.api.serializers.photo import PhotoSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def create_photo(request, user_id=None, point_id=None):
    """
    Endpoint to upload a photo.
    Must provide image + (user or point, not both).
    """
    data = request.data.copy()
    if user_id:
        data['user'] = user_id
    elif point_id:
        data['point'] = point_id
    serializer = PhotoSerializer(data=data)
    if serializer.is_valid():
        photo = serializer.save()
        return Response(PhotoSerializer(photo).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['PUT'])
# @permission_classes([IsAuthenticated])
# def update_photo
