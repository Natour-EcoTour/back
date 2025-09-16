"""
Views for user authentication and management.
"""
import logging
import threading

from smtplib import SMTPException

from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from django_ratelimit.decorators import ratelimit

from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from natour.api.serializers.user import CreateUserSerializer
from natour.api.models import CustomUser
from natour.api.utils.get_ip import get_client_ip
from natour.api.schemas.auth_schemas import (
    login_schema,
    create_user_schema,
    get_refresh_token_schema
)


logger = logging.getLogger("django")


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):  # pylint: disable=abstract-method
    """
    Custom serializer for obtaining JWT tokens with additional user information.
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['username'] = user.username
        token['email'] = user.email
        token['role'] = user.role.name

        return token


class MyTokenObtainPairView(TokenObtainPairView):
    """
    Custom view for obtaining JWT tokens using the custom serializer.
    """
    serializer_class = MyTokenObtainPairSerializer


@create_user_schema
@api_view(['POST'])
@permission_classes([AllowAny])
def create_user(request):
    """
    Endpoint to create a new user.
    """
    email = request.data.get('email')
    ip = get_client_ip(request)

    logger.info(
        "User creation request received for email: %s from IP: %s.",
        email, ip
    )

    if not request.data:
        return Response(
            {"detail": "Dados obrigatórios não fornecidos."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not email:
        return Response(
            {"detail": "E-mail é obrigatório."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not cache.get(f'verified_email:{email}'):
        logger.warning(
            "User with email %s (IP: %s) tried creating account before email verification.",
            email, ip
        )
        return Response(
            {"detail": "Você precisa validar seu e-mail antes de criar a conta."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        with transaction.atomic():
            cache.delete(f'verified_email:{email}')

            serializer = CreateUserSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()

                if user.role and user.role.name == 'master':
                    user.is_staff = True
                    user.is_superuser = True
                    user.save(update_fields=['is_staff', 'is_superuser'])

                logger.info(
                    "User created successfully: %s (ID: %s, IP: %s).",
                    user.username, user.id, ip
                )

                try:
                    html_content = render_to_string(
                        'email_templates/user_registration.html',
                        {'username': user.username}
                    )

                    def send_welcome_email():
                        try:
                            msg = EmailMultiAlternatives(
                                subject="Natour - Conta criada com sucesso",
                                body="Bem-vindo(a) ao Natour!",
                                from_email="natourproject@gmail.com",
                                to=[user.email],
                            )
                            msg.attach_alternative(html_content, "text/html")
                            msg.send()
                            logger.info(
                                "Welcome email sent successfully to %s (ID: %s).",
                                user.email, user.id
                            )
                        except SMTPException as e:
                            logger.error(
                                "Failed to send welcome email to %s (ID: %s): %s",
                                user.email, user.id, str(e)
                            )

                    threading.Thread(target=send_welcome_email,
                                     daemon=True).start()

                except Exception as e:
                    logger.error(
                        "Failed to start welcome email thread for user %s (ID: %s): %s",
                        user.email, user.id, str(e)
                    )

                return Response(CreateUserSerializer(user).data, status=status.HTTP_201_CREATED)

            logger.warning(
                "User creation failed validation for email %s (IP: %s): %s",
                email, ip, serializer.errors
            )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(
            "User creation failed for email %s (IP: %s): %s",
            email, ip, str(e)
        )
        return Response(
            {"detail": "Erro interno do servidor."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@login_schema
@api_view(['POST'])
@permission_classes([AllowAny])
@ratelimit(key='ip', rate='5/m', block=True)
def login(request):
    """
    Endpoint for user login with optional 'remember me' functionality.
    """
    email = request.data.get('email')
    password = request.data.get('password')
    remember_me = request.data.get('remember_me', False)
    ip = get_client_ip(request)

    logger.info(
        "Login attempt received for email: %s from IP: %s.",
        email, ip
    )

    if not request.data:
        return Response(
            {"detail": "Dados obrigatórios não fornecidos."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not email or not password:
        logger.warning(
            "Login attempt with missing credentials from IP: %s.",
            ip
        )
        return Response(
            {"error": "E-mail e senha são obrigatórios."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = (CustomUser.objects
                .select_related('role')
                .only('id', 'username', 'email', 'is_active', 'last_login', 'role__name')
                .get(email=email))

    except ObjectDoesNotExist:
        logger.warning(
            "Login failed: user not found for email %s (IP: %s).",
            email, ip
        )
        return Response(
            {"error": "E-mail ou senha incorretos."},
            status=status.HTTP_401_UNAUTHORIZED
        )

    if user.check_password(password):
        if not user.is_active:
            logger.warning(
                "Login failed: user %s (ID: %s) is inactive (IP: %s).",
                user.username, user.id, ip
            )
            return Response(
                {"error": "Conta desativada."},
                status=status.HTTP_403_FORBIDDEN
            )

        user.save(update_fields=['last_login'])

        refresh = RefreshToken.for_user(user)

        with transaction.atomic():
            if remember_me:
                remember_me_settings = getattr(settings, 'REMEMBER_ME_JWT', {})
                access_lifetime = remember_me_settings.get(
                    'ACCESS_TOKEN_LIFETIME')
                refresh_lifetime = remember_me_settings.get(
                    'REFRESH_TOKEN_LIFETIME')

                if access_lifetime:
                    refresh.access_token.set_exp(lifetime=access_lifetime)
                if refresh_lifetime:
                    refresh.set_exp(lifetime=refresh_lifetime)

        logger.info(
            "Login successful for user %s (ID: %s, IP: %s). Remember me: %s",
            user.username, user.id, ip, remember_me
        )

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role.name,
            },
            "remember_me": remember_me
        }, status=status.HTTP_200_OK)

    logger.warning(
        "Login failed: invalid password for email %s (IP: %s).",
        email, ip
    )
    return Response(
        {"error": "E-mail ou senha incorretos."},
        status=status.HTTP_401_UNAUTHORIZED
    )


@get_refresh_token_schema
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_refresh_token(request):
    """
    View to obtain a new refresh token from logged in user.
    """
    user = request.user
    ip = get_client_ip(request)

    logger.info(
        "Refresh token request from user %s (ID: %s, IP: %s).",
        user.username, user.id, ip
    )

    try:
        if not user.is_active:
            logger.warning(
                "Refresh token denied: user %s (ID: %s) is inactive (IP: %s).",
                user.username, user.id, ip
            )
            return Response(
                {"detail": "Conta desativada."},
                status=status.HTTP_403_FORBIDDEN
            )

        refresh_token = RefreshToken.for_user(user)

        logger.info(
            "Refresh token generated successfully for user %s (ID: %s, IP: %s).",
            user.username, user.id, ip
        )

        return Response({
            "refresh": str(refresh_token),
            "access": str(refresh_token.access_token)
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(
            "Failed to generate refresh token for user %s (ID: %s, IP: %s): %s",
            user.username, user.id, ip, str(e)
        )
        return Response(
            {"detail": "Erro interno do servidor."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
