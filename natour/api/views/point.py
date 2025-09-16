"""
Views for managing points in the Natour API.
"""
# pylint: disable=no-member
import logging

from smtplib import SMTPException

from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.db import transaction
from django_ratelimit.decorators import ratelimit
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import permission_classes

from natour.api.pagination import CustomPagination
from natour.api.utils.logging_decorators import api_logger, log_validation_error
from natour.api.serializers import user
from natour.api.serializers.point import (CreatePointSerializer, PointInfoSerializer,
                                          PointOnMapSerializer,
                                          PointApprovalSerializer, PointStatusUser,
                                          PointMapSearchSerializer)
from natour.api.models import Point
from natour.api.schemas.point_schemas import (
    create_point_schema,
    get_point_info_schema,
    get_all_points_schema,
    show_points_on_map_schema,
    point_approval_schema,
    search_point_schema,
    change_point_status_schema,
    delete_point_schema,
    delete_my_point_schema,
    add_view_schema,
    edit_point_schema
)

from natour.api.utils.get_ip import get_client_ip

logger = logging.getLogger("django")


@create_point_schema
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@api_logger("point_creation")
def create_point(request):
    """
    Create a new point.
    """
    user = request.user
    ip = get_client_ip(request)

    if not request.data:
        return Response(
            {"detail": "Dados obrigatórios não fornecidos."},
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer = CreatePointSerializer(data=request.data)
    if serializer.is_valid():
        with transaction.atomic():
            point = serializer.save(user=user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@point_approval_schema
@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsAdminUser])
@api_logger("point_approval")
def point_approval(request, point_id):
    """
    Approve or reject a point created by a user.
    """
    user = request.user
    ip = get_client_ip(request)

    if not request.data:
        return Response(
            {"detail": "Dados obrigatórios não fornecidos."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        with transaction.atomic():
            point = Point.objects.select_for_update().get(id=point_id)
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
                    user.username, user.id, point_id, previous_status, previous_is_active, new_status, new_is_active
                )
                return Response(serializer.data, status=status.HTTP_200_OK)

            logger.warning(
                "Admin '%s' (ID: %s) failed to change Point ID: %s status. Errors: %s",
                user.username, user.id, point_id, serializer.errors
            )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Point.DoesNotExist:
        logger.warning(
            "Admin '%s' (ID: %s) attempted to update non-existent Point ID: %s.",
            user.username, user.id, point_id
        )
        return Response(
            {"detail": "Ponto não encontrado."},
            status=status.HTTP_404_NOT_FOUND
        )


@get_point_info_schema
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@api_logger("point_info_retrieval")
def get_point_info(request, point_id):
    """
    Get information about a specific point.
    """
    try:
        point = (Point.objects
                 .select_related('user')
                 .prefetch_related('photos', 'reviews__user')
                 .get(id=point_id))

        serializer = PointInfoSerializer(point)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Point.DoesNotExist:
        logger.warning(
            "Attempted to retrieve non-existent Point ID: %s.",
            point_id
        )
        return Response(
            {"detail": "Ponto não encontrado."},
            status=status.HTTP_404_NOT_FOUND
        )


@get_all_points_schema
@vary_on_headers("Authorization")
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
@api_logger("all_points_retrieval")
def get_all_points(request):
    """
    Get all points created by all users.
    """
    if 'page' not in request.query_params:
        return Response(
            {"detail": "Você deve fornecer o parâmetro de paginação ?page=N."},
            status=status.HTTP_400_BAD_REQUEST
        )

    queryset = (Point.objects
                .select_related('user')
                .only('id', 'name', 'description', 'latitude', 'longitude',
                      'point_type', 'status', 'is_active', 'created_at',
                      'avg_rating', 'user_id', 'user__username'))

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


@change_point_status_schema
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@api_logger("point_status_change")
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


@delete_point_schema
@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
@api_logger("point_deletion")
def delete_point(request, point_id):
    """
    Delete a point.
    """
    point = get_object_or_404(Point, id=point_id)
    user = point.user

    html_content = render_to_string(
        'email_templates/delete_point.html',
        {
            'username': user.username,
            'point_name': point.name,
        }
    )

    try:
        msg = EmailMultiAlternatives(
            subject="Natour - Ponto Removido",
            body="Seu ponto foi removido.",
            from_email="natourproject@gmail.com",
            to=[user.email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        logger.info(
            "Point deletion email sent to '%s' (user ID: %s).",
            user.email, user.id
        )
    except SMTPException as e:
        logger.error(
            "Failed to send point deletion email to '%s' (user ID: %s). Error: %s",
            user.email, user.id, str(e)
        )
        return Response(
            {"detail": f"Erro ao enviar email: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    point.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@delete_my_point_schema
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@api_logger("my_point_deletion")
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

    return Response(status=status.HTTP_204_NO_CONTENT)


@add_view_schema
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@api_logger("point_view_increment")
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


@edit_point_schema
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@api_logger("point_editing")
def edit_point(request, point_id):
    """
    Edit a point created by the authenticated user.
    """
    user = request.user
    logger.info(
        "User '%s' (ID: %s) requested to edit Point ID: %s.",
        user.username, user.id, point_id
    )

    if not request.data:
        return Response(
            {"detail": "Dados obrigatórios não fornecidos."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        with transaction.atomic():
            point = Point.objects.select_for_update().get(id=point_id, user=user)

            serializer = CreatePointSerializer(
                point, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                logger.info(
                    "User '%s' (ID: %s) edited Point ID: %s successfully.",
                    user.username, user.id, point_id
                )
                return Response(serializer.data, status=status.HTTP_200_OK)

            logger.warning(
                "User '%s' (ID: %s) failed to edit Point ID: %s due to validation errors: %s",
                user.username, user.id, point_id, serializer.errors
            )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Point.DoesNotExist:
        logger.warning(
            "User '%s' (ID: %s) attempted to edit non-existent or unauthorized Point ID: %s.",
            user.username, user.id, point_id
        )
        return Response(
            {"detail": "Ponto não encontrado."},
            status=status.HTTP_404_NOT_FOUND
        )


@show_points_on_map_schema
@cache_page(60)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@api_logger("points_map_view")
def show_points_on_map(request):
    """
    Get all points to display on the map.
    """
    queryset = (Point.objects
                .filter(is_active=True, status=True)
                .only('id', 'name', 'latitude', 'longitude', 'point_type')
                .order_by('name'))

    if not queryset.exists():
        return Response(
            {"detail": "Nenhum ponto encontrado."},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = PointOnMapSerializer(queryset, many=True)

    logger.info(
        "Map points retrieved successfully. Count: %d",
        len(serializer.data)
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


@search_point_schema
@cache_page(60)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@api_logger("point_search")
def search_point(request):
    """
    Search point by name.
    """
    search_name = request.query_params.get("name", "").strip()

    if not search_name:
        return Response(
            {"detail": "Parâmetro 'name' é obrigatório para a busca."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if len(search_name) < 2:
        return Response(
            {"detail": "Nome deve ter pelo menos 2 caracteres."},
            status=status.HTTP_400_BAD_REQUEST
        )

    queryset = (Point.objects
                .filter(is_active=True, name__icontains=search_name)
                .only('id', 'name', 'latitude', 'longitude', 'point_type')
                .order_by('name'))

    serializer = PointMapSearchSerializer(queryset, many=True)

    if serializer.data:
        logger.info(
            "Point search for '%s' returned %d results.",
            search_name, len(serializer.data)
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    logger.info(
        "Point search for '%s' returned no results.",
        search_name
    )
    return Response(
        {"detail": "Nenhum ponto encontrado."},
        status=status.HTTP_404_NOT_FOUND
    )
