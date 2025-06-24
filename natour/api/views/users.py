"""
Views for user management in the Natour API.
"""
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers

# from django_ratelimit.decorators import ratelimit
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import permission_classes

from natour.api.serializers.user import CustomUserInfoSerializer, UpdateUserSerializer


@cache_page(60)
@vary_on_headers("Authorization")
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_info(request):
    """
    Endpoint to get the authenticated user's information.
    """
    user = request.user
    return Response(CustomUserInfoSerializer(user).data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_my_account(request):
    """
    Endpoint to delete the authenticated user's account.
    """
    user = request.user
    user.delete()
    return Response({"detail": "Conta deletada com sucesso."}, status=status.HTTP_204_NO_CONTENT)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_my_info(request):
    """
    Endpoint to update the authenticated user's information.
    """
    user = request.user
    serializer = UpdateUserSerializer(
        user, data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
