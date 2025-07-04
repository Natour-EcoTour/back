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

logger = logging.getLogger("django")


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_point(request):
    """
    Create a new point.
    """
    user = request.user
    logger.info(
        "Received request to create a point.",
        extra={
            "action": "create_point",
            "user_id": user.id,
            "username": user.username,
            "ip": request.META.get("REMOTE_ADDR"),
        }
    )

    serializer = CreatePointSerializer(data=request.data)
    if serializer.is_valid():
        point = serializer.save(user=user)
        logger.info(
            "Point created successfully.",
            extra={
                "action": "create_point",
                "user_id": user.id,
                "username": user.username,
                "point_id": point.id,
                "result": "success",
                "ip": request.META.get("REMOTE_ADDR")
            }
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    logger.warning(
        "Failed to create point due to validation errors.",
        extra={
            "action": "create_point",
            "user_id": user.id,
            "username": user.username,
            "errors": serializer.errors,
            "result": "validation_error",
            "ip": request.META.get("REMOTE_ADDR")
        }
    )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsAdminUser])
def point_approval(request, point_id):
    """
    Approve or reject a point created by a user.
    """
    user = request.user
    logger.info(
        "Received request to approve/reject a point.",
        extra={
            "action": "point_approval",
            "admin_user_id": user.id,
            "admin_username": user.username,
            "point_id": point_id,
            "ip": request.META.get("REMOTE_ADDR")
        }
    )

    point = get_object_or_404(Point, id=point_id)
    new_status = request.data.get('status')
    new_is_active = request.data.get('is_active')

    if new_status is None or new_is_active is None:
        logger.warning(
            "Missing required status or is_active fields.",
            extra={
                "action": "point_approval",
                "admin_user_id": user.id,
                "admin_username": user.username,
                "point_id": point_id,
                "result": "missing_fields",
                "ip": request.META.get("REMOTE_ADDR")
            }
        )
        return Response(
            {"detail": "Você deve fornecer 'status' e 'is_active'."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if point.status == new_status and point.is_active == new_is_active:
        state_text = "ativo" if new_status and new_is_active else "inativo"
        logger.info(
            "Point already in requested state.",
            extra={
                "action": "point_approval",
                "admin_user_id": user.id,
                "admin_username": user.username,
                "point_id": point_id,
                "requested_status": new_status,
                "requested_is_active": new_is_active,
                "result": "no_change_needed",
                "ip": request.META.get("REMOTE_ADDR")
            }
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
            "Point approval/rejection processed successfully.",
            extra={
                "action": "point_approval",
                "admin_user_id": user.id,
                "admin_username": user.username,
                "point_id": point_id,
                "new_status": new_status,
                "new_is_active": new_is_active,
                "result": "success",
                "ip": request.META.get("REMOTE_ADDR")
            }
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    logger.warning(
        "Point approval/rejection failed validation.",
        extra={
            "action": "point_approval",
            "admin_user_id": user.id,
            "admin_username": user.username,
            "point_id": point_id,
            "errors": serializer.errors,
            "result": "validation_error",
            "ip": request.META.get("REMOTE_ADDR")
        }
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
    logger.info(
        "Received request to change point status.",
        extra={
            "action": "change_point_status",
            "user_id": user.id,
            "username": user.username,
            "point_id": point_id,
            "ip": request.META.get("REMOTE_ADDR")
        }
    )

    target_point = get_object_or_404(Point, id=point_id, user=user)

    previous_status = target_point.is_active

    target_point.is_active = not target_point.is_active

    serializer = PointStatusUser(target_point, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        logger.info(
            "Point status changed successfully.",
            extra={
                "action": "change_point_status",
                "user_id": user.id,
                "username": user.username,
                "point_id": point_id,
                "previous_status": previous_status,
                "new_status": target_point.is_active,
                "result": "success",
                "ip": request.META.get("REMOTE_ADDR")
            }
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    logger.warning(
        "Failed to change point status due to validation errors.",
        extra={
            "action": "change_point_status",
            "user_id": user.id,
            "username": user.username,
            "point_id": point_id,
            "errors": serializer.errors,
            "result": "validation_error",
            "ip": request.META.get("REMOTE_ADDR")
        }
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
        extra={
            "action": "delete_my_point",
            "user_id": user.id,
            "username": user.username,
            "point_id": point_id,
            "ip": request.META.get("REMOTE_ADDR")
        }
    )

    point = get_object_or_404(Point, id=point_id, user=user)

    point.delete()

    logger.info(
        "Point deleted successfully.",
        extra={
            "action": "delete_my_point",
            "user_id": user.id,
            "username": user.username,
            "point_id": point_id,
            "result": "success",
            "ip": request.META.get("REMOTE_ADDR")
        }
    )

    return Response({"detail": "Ponto excluído com sucesso."}, status=status.HTTP_204_NO_CONTENT)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def add_view(request, point_id):
    """
    Increment the view count of a point.
    """
    user = request.user
    logger.info(
        "Received request to increment point view count.",
        extra={
            "action": "add_view",
            "user_id": user.id,
            "username": user.username,
            "point_id": point_id,
            "ip": request.META.get("REMOTE_ADDR")
        }
    )

    point = get_object_or_404(Point, id=point_id)

    previous_views = point.views
    point.views += 1
    point.save()

    logger.info(
        "Point view count incremented successfully.",
        extra={
            "action": "add_view",
            "user_id": user.id,
            "username": user.username,
            "point_id": point_id,
            "previous_views": previous_views,
            "new_views": point.views,
            "result": "success",
            "ip": request.META.get("REMOTE_ADDR")
        }
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
        extra={
            "action": "edit_point",
            "user_id": user.id,
            "username": user.username,
            "point_id": point_id,
            "ip": request.META.get("REMOTE_ADDR")
        }
    )

    point = get_object_or_404(Point, id=point_id, user=user)

    serializer = CreatePointSerializer(point, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        logger.info(
            "Point edited successfully.",
            extra={
                "action": "edit_point",
                "user_id": user.id,
                "username": user.username,
                "point_id": point_id,
                "result": "success",
                "ip": request.META.get("REMOTE_ADDR")
            }
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    logger.warning(
        "Failed to edit point due to validation errors.",
        extra={
            "action": "edit_point",
            "user_id": user.id,
            "username": user.username,
            "point_id": point_id,
            "errors": serializer.errors,
            "result": "validation_error",
            "ip": request.META.get("REMOTE_ADDR")
        }
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
