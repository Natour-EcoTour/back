"""
Views for user management in the Natour API.
"""
import logging

from smtplib import SMTPException
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

# from django_ratelimit.decorators import ratelimit
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.generics import get_object_or_404

from natour.api.pagination import CustomPagination
from natour.api.models import CustomUser
from natour.api.serializers.user import (CustomUserInfoSerializer, UpdateUserSerializer,
                                         AllUsersSerializer, UserStatusSerializer,
                                         UserPasswordSerializer)
from natour.api.serializers.point import PointInfoSerializer

logger = logging.getLogger("django")


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
    logger.info(
        "Received request to delete user account.",
        extra={
            "action": "delete_my_account",
            "user_id": user.id,
            "username": user.username,
            "ip": request.META.get("REMOTE_ADDR")
        }
    )

    user.delete()

    logger.info(
        "User account deleted successfully.",
        extra={
            "action": "delete_my_account",
            "user_id": user.id,
            "username": user.username,
            "result": "success",
            "ip": request.META.get("REMOTE_ADDR")
        }
    )

    return Response({"detail": "Conta deletada com sucesso."}, status=status.HTTP_204_NO_CONTENT)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
def delete_user_account(request, user_id):
    """
    Endpoint to delete a user's account by an admin.
    """
    admin = request.user
    target_user = get_object_or_404(CustomUser, id=user_id)

    logger.info(
        "Received request to delete another user's account.",
        extra={
            "action": "delete_user_account",
            "admin_user_id": admin.id,
            "admin_username": admin.username,
            "target_user_id": target_user.id,
            "target_username": target_user.username,
            "ip": request.META.get("REMOTE_ADDR")
        }
    )

    html_content = render_to_string(
        'email_templates/delete_user_account.html',
        {
            'username': target_user.username
        }
    )

    try:
        msg = EmailMultiAlternatives(
            subject="Natour - Conta excluída",
            body="Sua conta foi excluída.",
            from_email="natourproject@gmail.com",
            to=[target_user.email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
    except SMTPException as e:
        logger.error(
            "Failed to send account deletion email.",
            extra={
                "action": "delete_user_account",
                "admin_user_id": admin.id,
                "admin_username": admin.username,
                "target_user_id": target_user.id,
                "target_username": target_user.username,
                "result": "email_send_failed",
                "error": str(e),
                "ip": request.META.get("REMOTE_ADDR")
            }
        )
        return Response(
            {"detail": f"Erro ao enviar email: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    target_user.delete()

    logger.info(
        "User account deleted by admin successfully.",
        extra={
            "action": "delete_user_account",
            "admin_user_id": admin.id,
            "admin_username": admin.username,
            "target_user_id": target_user.id,
            "target_username": target_user.username,
            "result": "success",
            "ip": request.META.get("REMOTE_ADDR")
        }
    )

    return Response({"detail": "Conta deletada com sucesso."}, status=status.HTTP_204_NO_CONTENT)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_my_info(request):
    """
    Endpoint to update the authenticated user's information.
    """
    user = request.user
    logger.info(
        "Received request to update user profile.",
        extra={
            "action": "update_my_info",
            "user_id": user.id,
            "username": user.username,
            "ip": request.META.get("REMOTE_ADDR")
        }
    )

    serializer = UpdateUserSerializer(user, data=request.data)

    if serializer.is_valid():
        serializer.save()
        logger.info(
            "User profile updated successfully.",
            extra={
                "action": "update_my_info",
                "user_id": user.id,
                "username": user.username,
                "result": "success",
                "ip": request.META.get("REMOTE_ADDR")
            }
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    logger.warning(
        "Failed to update user profile due to validation errors.",
        extra={
            "action": "update_my_info",
            "user_id": user.id,
            "username": user.username,
            "errors": serializer.errors,
            "result": "validation_error",
            "ip": request.META.get("REMOTE_ADDR")
        }
    )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@cache_page(60)
@vary_on_headers("Authorization")
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_all_users(request):
    """
    Endpoint to get a list of all users.
    """
    if 'page' not in request.query_params:
        return Response(
            {"detail": "Você deve fornecer o parâmetro de paginação ?page=N."},
            status=status.HTTP_400_BAD_REQUEST
        )

    queryset = CustomUser.objects.all()

    queryset = queryset.exclude(role__id=2)

    username = request.query_params.get('username')
    if username:
        queryset = queryset.filter(username__istartswith=username)
    email = request.query_params.get('email')
    if email:
        queryset = queryset.filter(email__istartswith=email)

    queryset = queryset.order_by('username')

    total_users = queryset.count()

    paginator = CustomPagination()
    page = paginator.paginate_queryset(queryset, request)
    if page:
        serializer = AllUsersSerializer(page, many=True)
        response = paginator.get_paginated_response(serializer.data)
        response.data['total_users'] = total_users
        return response
    return Response(
        {"detail": "Nenhm resultado encontrado.", "total_users": 0},
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsAdminUser])
def change_user_status(request, user_id):
    """
    Endpoint to change the status of a user.
    """
    admin = request.user
    target_user = get_object_or_404(CustomUser, id=user_id)

    logger.info(
        "Received request to change user status.",
        extra={
            "action": "change_user_status",
            "admin_user_id": admin.id,
            "admin_username": admin.username,
            "target_user_id": target_user.id,
            "target_username": target_user.username,
            "old_status": target_user.is_active,
            "ip": request.META.get("REMOTE_ADDR")
        }
    )

    target_user.is_active = not target_user.is_active
    serializer = UserStatusSerializer(
        target_user, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

        logger.info(
            "User status changed successfully.",
            extra={
                "action": "change_user_status",
                "admin_user_id": admin.id,
                "admin_username": admin.username,
                "target_user_id": target_user.id,
                "target_username": target_user.username,
                "new_status": target_user.is_active,
                "result": "success",
                "ip": request.META.get("REMOTE_ADDR")
            }
        )

        html_content = render_to_string(
            'email_templates/user_status_change.html',
            {
                'username': target_user.username,
                'status_class': 'ativo' if target_user.is_active else 'inativo',
                'is_active': 'Ativada' if target_user.is_active else 'Desativada',
                'deactivation_reason': target_user.deactivation_reason
            }
        )

        try:
            msg = EmailMultiAlternatives(
                subject="Natour - Status da Conta",
                body=f"Sua conta foi {'ativada' if target_user.is_active else 'desativada'}.",
                from_email="natourproject@gmail.com",
                to=[target_user.email],
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        except SMTPException as e:
            logger.error(
                "Failed to send user status change email.",
                extra={
                    "action": "change_user_status",
                    "admin_user_id": admin.id,
                    "admin_username": admin.username,
                    "target_user_id": target_user.id,
                    "target_username": target_user.username,
                    "result": "email_send_failed",
                    "error": str(e),
                    "ip": request.META.get("REMOTE_ADDR")
                }
            )
            return Response(
                {"detail": f"Erro ao enviar email: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(serializer.data, status=status.HTTP_200_OK)

    logger.warning(
        "Failed to change user status due to validation errors.",
        extra={
            "action": "change_user_status",
            "admin_user_id": admin.id,
            "admin_username": admin.username,
            "target_user_id": target_user.id,
            "target_username": target_user.username,
            "errors": serializer.errors,
            "result": "validation_error",
            "ip": request.META.get("REMOTE_ADDR")
        }
    )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@cache_page(60)
@vary_on_headers("Authorization")
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_user_points(request, user_id):
    """
    Endpoint to get all points created by a specific user.
    """
    user = get_object_or_404(CustomUser, id=user_id)
    points = user.points.all().order_by('-created_at')

    point_name = request.query_params.get('name')
    if point_name:
        points = points.filter(name__istartswith=point_name)

    if not points:
        return Response(
            {"detail": "Nenhum ponto encontrado para este usuário."},
            status=status.HTTP_404_NOT_FOUND
        )

    points_amount = points.count()

    serializer = PointInfoSerializer(points, many=True)
    return Response({
        "count": points_amount,
        "points": serializer.data
    }, status=status.HTTP_200_OK)


@cache_page(60)
@vary_on_headers("Authorization")
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_points(request):
    """
    Endpoint to get all points created by the authenticated user.
    """

    user = request.user
    points = user.points.all().order_by('-created_at')

    point_name = request.query_params.get('name')
    if point_name:
        points = points.filter(name__istartswith=point_name)

    if not points.exists():
        return Response(
            {"detail": "Nenhum ponto encontrado."},
            status=status.HTTP_404_NOT_FOUND
        )

    points_amount = points.count()
    serializer = PointInfoSerializer(points, many=True)
    return Response({
        "count": points_amount,
        "points": serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_my_password(request):
    """
    Endpoint to update the authenticated user's password.
    """

    user = request.user

    serializer = UserPasswordSerializer(data=request.data)

    if serializer.is_valid():
        old_password = serializer.validated_data.get('old_password')

        if not user.check_password(old_password):
            return Response(
                {"detail": "Senha antiga incorreta."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response(
            {"detail": "Senha atualizada com sucesso."},
            status=status.HTTP_200_OK
        )
    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )
