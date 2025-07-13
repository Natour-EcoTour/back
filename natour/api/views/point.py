"""
Views for managing points in the Natour API.
"""
# pylint: disable=no-member
import logging

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
                                          PointOnMapSerializer,
                                          PointApprovalSerializer, PointStatusUser)
from natour.api.models import Point

from natour.api.utils.get_ip import get_client_ip

logger = logging.getLogger("django")


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_point(request):
    """
    Create a new point.
    """
    user = request.user
    ip = get_client_ip(request)
    logger.info(
        "User '%s' (ID: %s, IP: %s) requested to create a point.",
        user.username,
        user.id,
        ip,
    )

    serializer = CreatePointSerializer(data=request.data)
    if serializer.is_valid():
        point = serializer.save(user=user)
        logger.info(
            "Point created successfully by user '%s' (ID: %s). Point ID: %s, Name: '%s'",
            user.username,
            user.id,
            point.id,
            getattr(point, "name", "<no name>"),
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    logger.warning(
        "User '%s' (ID: %s) failed to create point due to validation errors: %s",
        user.username,
        user.id,
        serializer.errors,
    )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsAdminUser])
def point_approval(request, point_id):
    """
    Approve or reject a point created by a user.
    """
    user = request.user
    ip = get_client_ip(request)
    logger.info(
        "Admin '%s' (ID: %s, IP: %s) requested approval/rejection for Point ID: %s.",
        user.username, user.id, ip, point_id
    )

    point = get_object_or_404(Point, id=point_id)
    previous_status = point.status
    previous_is_active = point.is_active

    new_status = request.data.get('status')
    new_is_active = request.data.get('is_active')

    if new_status is None or new_is_active is None:
        logger.warning(
            "Admin '%s' (ID: %s) - Missing required status or is_active fields for Point ID: %s.",
            user.username, user.id, point_id
        )
        return Response(
            {"detail": "Você deve fornecer 'status' e 'is_active'."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if point.status == new_status and point.is_active == new_is_active:
        state_text = "ativo" if new_status and new_is_active else "inativo"
        logger.info(
            "Admin '%s' (ID: %s) - Point ID: %s already in requested state: %s.",
            user.username, user.id, point_id, state_text
        )
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
        logger.info(
            "Admin '%s' (ID: %s) changed Point ID: %s status from (%s, %s) to (%s, %s) successfully.",
            user.username, user.id, point_id,
            previous_status, previous_is_active,
            new_status, new_is_active
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    logger.warning(
        "Admin '%s' (ID: %s) failed to change Point ID: %s status. Errors: %s",
        user.username, user.id, point_id, serializer.errors
    )
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
@permission_classes([IsAuthenticated, IsAdminUser])
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
    user = request.user
    ip = get_client_ip(request)

    logger.info(
        "User '%s' (ID: %s) from IP: %s requested status change for Point ID: %s.",
        user.username,
        user.id,
        ip,
        point_id
    )

    target_point = get_object_or_404(Point, id=point_id, user=user)
    previous_status = target_point.is_active
    new_status = not previous_status

    target_point.is_active = new_status

    serializer = PointStatusUser(target_point, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        logger.info(
            "User '%s' (ID: %s) changed Point ID: %s status from %s to %s successfully.",
            user.username,
            user.id,
            point_id,
            previous_status,
            new_status
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    logger.warning(
        "User '%s' (ID: %s) failed to change Point ID: %s status from %s to %s. Errors: %s",
        user.username,
        user.id,
        point_id,
        previous_status,
        new_status,
        serializer.errors
    )
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
    user = request.user
    logger.info(
        "Received request to delete a point.",
    )

    point = get_object_or_404(Point, id=point_id, user=user)

    point.delete()

    logger.info(
        "Point deleted successfully.",
    )

    return Response({"detail": "Ponto excluído com sucesso."}, status=status.HTTP_204_NO_CONTENT)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def add_view(request, point_id):
    """
    Increment the view count of a point.
    """
    user = request.user

    point = get_object_or_404(Point, id=point_id)

    previous_views = point.views
    point.views += 1
    point.save()

    ip = get_client_ip(request)

    logger.info(
        "User '%s' (ID: %s) from IP: %s incremented view count for Point ID: %s | Previous views: %d | New views: %d",
        user.username,
        user.id,
        ip,
        point_id,
        previous_views,
        point.views,
    )

    return Response({"views": point.views}, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_point(request, point_id):
    """
    Edit a point created by the authenticated user.
    """
    user = request.user
    logger.info(
        "Received request to edit a point.",
    )

    point = get_object_or_404(Point, id=point_id, user=user)

    serializer = CreatePointSerializer(point, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        logger.info(
            "Point edited successfully.",
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    logger.warning(
        "Failed to edit point due to validation errors.",
    )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ADICIONAR EMAIL
# @api_view(['PUT'])
# @permission_classes([IsAuthenticated, IsAdminUser])
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
