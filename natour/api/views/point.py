"""
Views for managing points in the Natour API.
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
                                          PointStatusSerializer, PointOnMapSerializer,
                                          PointApprovalSerializer, PointStatusUser)
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


@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsAdminUser])
def point_approval(request, point_id):
    """
    Approve or reject a point created by a user.
    """
    point = get_object_or_404(Point, id=point_id)

    new_status = request.data.get('status')
    new_is_active = request.data.get('is_active')

    if new_status is None or new_is_active is None:
        return Response(
            {"detail": "Você deve fornecer 'status' e 'is_active'."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if point.status == new_status and point.is_active == new_is_active:
        state_text = "ativo" if new_status and new_is_active else "inativo"
        return Response(
            {"detail": f"Este ponto já está {state_text}."},
            status=status.HTTP_400_BAD_REQUEST
        )

    point.status = new_status
    point.is_active = new_is_active

    serializer = PointApprovalSerializer(
        point, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

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

    status_param = request.query_params.get('status')
    if status_param is not None:
        if status_param.lower() == 'true':
            queryset = queryset.filter(status=True)
        elif status_param.lower() == 'false':
            queryset = queryset.filter(status=False)
        elif status_param.lower() == 'null' or status_param.lower() == 'none':
            queryset = queryset.filter(status__isnull=True)
        else:
            return Response(
                {"detail": "Parâmetro 'status' deve ser 'true', 'false', 'null' ou 'none'."},
                status=status.HTTP_400_BAD_REQUEST
            )

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
    target_point = get_object_or_404(Point, id=point_id, user=request.user)

    target_point.is_active = not target_point.is_active
    serializer = PointStatusUser(
        target_point, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ADICIONAR EMAIL


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


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def add_view(request, point_id):
    """
    Increment the view count of a point.
    """
    point = get_object_or_404(Point, id=point_id)

    point.views += 1
    point.save()

    return Response({"views": point.views}, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_point(request, point_id):
    """
    Edit a point created by the authenticated user.
    """
    point = get_object_or_404(Point, id=point_id, user=request.user)

    serializer = CreatePointSerializer(point, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ADICIONAR EMAIL
# @api_view(['PUT'])
# @permission_classes([IsAuthenticated])
# def change_point_status_master(request, point_id):
#     """
#     Change the status of a point.
#     """
#     target_point = get_object_or_404(Point, id=point_id)

#     target_point.is_active = not target_point.is_active
#     serializer = PointStatusSerializer(
#         target_point, data=request.data, partial=True)

#     if serializer.is_valid():
#         serializer.save()

#         return Response(serializer.data, status=status.HTTP_200_OK)

#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# ADICIONAR ENVIO DE EMAIL E VERIFICAÇÃO SE É MASTER...


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def show_points_on_map(request):
    """
    Get all points to display on the map.
    """
    queryset = Point.objects.filter(is_active=True).filter(
        status=True).order_by('name')

    if not queryset.exists():
        return Response(
            {"detail": "Nenhum ponto ativo encontrado."},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = PointOnMapSerializer(queryset, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
