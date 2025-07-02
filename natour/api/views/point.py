"""
a
"""

from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import permission_classes

from natour.api.serializers.point import CreatePointSerializer, PointInfoSerializer
from natour.api.models import Point


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_point(request):
    """
    Create a new point.
    """
    serializer = CreatePointSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_point_info(request, point_id):
    """
    Get information about a specific point.
    """
    point = get_object_or_404(Point, id=point_id)
    serializer = PointInfoSerializer(point)
    return Response(serializer.data, status=status.HTTP_200_OK)


# quantidade de pontos que o usuário tem e que tem como todo na plataforma
