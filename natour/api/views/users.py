"""
Views for user management in the Natour API.
"""

# from django_ratelimit.decorators import ratelimit
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import permission_classes

from natour.api.serializers.user import CustomUserInfoSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_info(request):
    """
    Endpoint to get the authenticated user's information.
    """
    user = request.user
    return Response(CustomUserInfoSerializer(user).data, status=status.HTTP_200_OK)
