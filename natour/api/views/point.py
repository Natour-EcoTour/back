"""
a
"""
# pylint: disable=no-member

from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import permission_classes

from natour.api.pagination import CustomPagination
from natour.api.serializers.point import (CreatePointSerializer, PointInfoSerializer,
                                          PointStatusSerializer)
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


@cache_page(60)
@vary_on_headers("Authorization")
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_points(request):
    """
    Get all points created by all users.
    """

    if 'page' not in request.query_params:
        return Response(
            {"detail": "Você deve fornecer o parâmetro de paginação ?page=N."},
            status=status.HTTP_400_BAD_REQUEST
        )

    queryset = Point.objects.all()

    point_name = request.query_params.get('name')
    if point_name:
        queryset = queryset.filter(name__istartswith=point_name)

    queryset = queryset.order_by('name')

    paginator = CustomPagination()
    page = paginator.paginate_queryset(queryset, request)
    if page:
        serializer = PointInfoSerializer(page, many=True)
        response = paginator.get_paginated_response(serializer.data)
        return response
    return Response(
        {"detail": "Nenhum resultado encontrado.", "total_points": 0},
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def change_point_status(request, point_id):
    """
    Change the status of a point.
    """
    target_point = get_object_or_404(Point, id=point_id)

    target_point.is_active = not target_point.is_active
    serializer = PointStatusSerializer(
        target_point, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
def delete_point(request, point_id):
    """
    Delete a point.
    """
    point = get_object_or_404(Point, id=point_id)

    point.delete()
    return Response({"detail": "Ponto excluído com sucesso."}, status=status.HTTP_204_NO_CONTENT)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_my_point(request, point_id):
    """
    Delete a point created by the authenticated user.
    """
    point = get_object_or_404(Point, id=point_id, user=request.user)

    point.delete()
    return Response({"detail": "Ponto excluído com sucesso."}, status=status.HTTP_204_NO_CONTENT)
