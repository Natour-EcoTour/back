"""
Views for handling photo uploads in the Natour API.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from cloudinary.uploader import destroy

from natour.api.models import Photo
from natour.api.serializers.photo import PhotoSerializer, PhotoIDSerializer


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


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_photo(request, photo_id, user_id=None, point_id=None):
    """Endpoint to update a photo.
    Must provide image + (user or point, not both).
    """
    data = request.data.copy()
    if user_id:
        data['user'] = user_id
    elif point_id:
        data['point'] = point_id
    try:
        photo = Photo.objects.get(id=photo_id) # pylint: disable=no-member
    except Photo.DoesNotExist: # pylint: disable=no-member
        return Response({'error': 'Photo not found.'}, status=404)

    # Verifica se está vindo uma nova imagem
    new_image = data.get('image', None)
    if new_image:
        # Deleta a imagem antiga do Cloudinary
        if photo.image:
            # Extrai o public_id do Cloudinary
            public_id = photo.image.public_id
            destroy(public_id)

    serializer = PhotoSerializer(photo, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def get_photo(request):
    """
    Endpoint
    """
    user_id = request.query_params.get('user_id')
    point_id = request.query_params.get('point_id')

    if not user_id and not point_id:
        return Response(
            {"detail": "You must provide at least 'user_id' or 'point_id' as query parameter."},
            status=status.HTTP_400_BAD_REQUEST
        )

    queryset = Photo.objects.all()  # pylint: disable=no-member

    if user_id:
        queryset = queryset.filter(user_id=user_id)
    if point_id:
        queryset = queryset.filter(point_id=point_id)

    serializer = PhotoIDSerializer(queryset, many=True)
    return Response(serializer.data)
