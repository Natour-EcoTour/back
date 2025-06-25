"""
Views for handling photo uploads in the Natour API.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import get_object_or_404
from cloudinary.uploader import destroy
from cloudinary.exceptions import Error as CloudinaryError

from natour.api.models import Photo, CustomUser, Point
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
        get_object_or_404(CustomUser, id=user_id)
        data['user'] = user_id
    elif point_id:
        get_object_or_404(Point, id=point_id)
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
        get_object_or_404(CustomUser, id=user_id)
        data['user'] = user_id
    elif point_id:
        get_object_or_404(Point, id=point_id)
        data['point'] = point_id

    photo = get_object_or_404(Photo, id=photo_id)

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

    if user_id:
        get_object_or_404(CustomUser, id=user_id)
    if point_id:
        get_object_or_404(Point, id=point_id)

    queryset = Photo.objects.all()  # pylint: disable=no-member

    if user_id:
        queryset = queryset.filter(user_id=user_id)
    if point_id:
        queryset = queryset.filter(point_id=point_id)

    serializer = PhotoIDSerializer(queryset, many=True)
    return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_photo(request):
    """
    Deletes multiple photos from Cloudinary and the database.
    Requires both 'ids' and 'public_ids' lists with the same length.
    Returns 400 Bad Request if any id doesn't exist or if there's a public_id mismatch.
    """
    ids = request.data.get('ids', [])
    public_ids = request.data.get('public_ids', [])

    if not ids or not public_ids:
        return Response(
            {'detail': 'É necessário "ids" e "public_ids".'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if len(ids) != len(public_ids):
        return Response(
            {'detail': '"ids" e "public_ids" devem ter o mesmo tamanho.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Query all matching photos at once
    photos = Photo.objects.filter(id__in=ids)  # pylint: disable=no-member
    if photos.count() != len(ids):
        return Response(
            {'detail': 'ID inexistente.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Build a lookup dict for validation
    photo_map = {photo.id: photo for photo in photos}

    for photo_id, public_id in zip(ids, public_ids):
        photo = photo_map.get(photo_id)
        if not photo or not photo.image or photo.image.public_id != public_id:
            return Response(
                {
                    'detail': f'Incompatibilidade ou ausência de ID public para ID photo {photo_id}.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

    # All valid: proceed to delete
    deleted_ids = []
    deleted_public_ids = []

    for photo_id, public_id in zip(ids, public_ids):
        photo = photo_map[photo_id]
        try:
            destroy(public_id)
        except CloudinaryError as e:
            return Response(
                {'detail': f'Error deleting Cloudinary image for ID {photo_id}: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        photo.delete()
        deleted_ids.append(photo_id)
        deleted_public_ids.append(public_id)

    return Response(
        {
            'deleted_ids': deleted_ids,
            'deleted_public_ids': deleted_public_ids
        },
        status=status.HTTP_204_NO_CONTENT
    )
