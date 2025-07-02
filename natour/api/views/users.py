"""
Views for user management in the Natour API.
"""
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
                                         AllUsersSerializer, UserStatusSerializer)
from natour.api.serializers.point import PointInfoSerializer


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


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
def delete_user_account(request, user_id):
    """
    Endpoint to delete a user's account by an admin.
    """
    target_user = get_object_or_404(CustomUser, id=user_id)

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
        return Response(
            {"detail": f"Erro ao enviar email: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    target_user.delete()

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


@cache_page(60)
@vary_on_headers("Authorization")
@api_view(['GET'])
@permission_classes([IsAuthenticated])
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

    paginator = CustomPagination()
    page = paginator.paginate_queryset(queryset, request)
    if page:
        serializer = AllUsersSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
    else:
        return Response(
            {"detail": "Nenhm resultado encontrado."},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsAdminUser])
def change_user_status(request, user_id):
    """
    Endpoint to change the status of a user.
    """
    target_user = get_object_or_404(CustomUser, id=user_id)

    target_user.is_active = not target_user.is_active
    serializer = UserStatusSerializer(
        target_user, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

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
            return Response(
                {"detail": f"Erro ao enviar email: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@cache_page(60)
@vary_on_headers("Authorization")
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_points(request, user_id):
    """
    Endpoint to get all points created by a specific user.
    """
    user = get_object_or_404(CustomUser, id=user_id)
    points = user.points.all()

    if not points:
        return Response(
            {"detail": "Nenhum ponto encontrado para este usuário."},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = PointInfoSerializer(points, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@cache_page(60)
@vary_on_headers("Authorization")
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_points(request):
    """
    Endpoint to get all points created by the authenticated user.
    """

    user = request.user
    points = user.points.all()
    points_amount = points.count()

    if not points:
        return Response(
            {"detail": "Nenhum ponto encontrado."},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = PointInfoSerializer(points, many=True)
    return Response({
        "count": points_amount,
        "points": serializer.data
    }, status=status.HTTP_200_OK)
