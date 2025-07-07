"""
Views for user authentication and management.
"""
import logging

from smtplib import SMTPException

from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist

from django_ratelimit.decorators import ratelimit

from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from natour.api.serializers.user import CreateUserSerializer, GenericUserSerializer
from natour.api.models import CustomUser

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


@api_view(['POST'])
@permission_classes([AllowAny])
def create_user(request):
    """
    Endpoint to create a new user.
    """
    email = request.data.get('email')
    logger.info(
        "Received user creation request.",
        extra={
            "email": email,
            "action": "create_user",
            "request_data": request.data
        }
    )

    if not cache.get(f'verified_email:{email}'):
        logger.warning(
            "User tried creating an account before code verification.",
            extra={
                "email": email,
                "action": "create_user",
                "result": "email_not_verified",
                "request_data": request.data
            }
        )
        return Response(
            {"detail": "Você precisa validar seu e-mail antes de criar a conta."},
            status=status.HTTP_400_BAD_REQUEST
        )

    cache.delete(f'verified_email:{email}')

    serializer = CreateUserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()

        if user.role and user.role.name == 'master':
            user.is_staff = True
            user.is_superuser = True
            user.save(update_fields=['is_staff', 'is_superuser'])

        logger.info(
            "User created successfully.",
            extra={
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "action": "create_user",
                "result": "success"
            }
        )

        html_content = render_to_string(
            'email_templates/user_registration.html',
            {
                'username': user.username
            }
        )

        try:
            msg = EmailMultiAlternatives(
                subject="Natour - Conta criada com sucesso",
                body="Bem-vindo(a) ao Natour!",
                from_email="natourproject@gmail.com",
                to=[user.email],
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        except SMTPException as e:
            logger.error(
                "Failed to send user registration email.",
                extra={
                    "user_id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "action": "create_user",
                    "result": "email_send_failed",
                    "error": str(e)
                }
            )
            return Response(
                {"detail": f"Erro ao enviar email: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        return Response(CreateUserSerializer(user).data, status=status.HTTP_201_CREATED)

    logger.warning(
        "User creation failed validation.",
        extra={
            "email": email,
            "action": "create_user",
            "result": "validation_error",
            "errors": serializer.errors,
            "request_data": request.data
        }
    )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
@ratelimit(key='ip', rate='5/m', block=True)
def login(request):
    """
    Endpoint for user login.
    """
    email = request.data.get('email')

    logger.info(
        "Login attempt received.",
        extra={
            "action": "login",
            "email": email,
            "ip": request.META.get("REMOTE_ADDR")
        }
    )
    try:
        user = CustomUser.objects.get(email=email)
    except ObjectDoesNotExist:
        logger.warning(
            "Login failed: user not found.",
            extra={
                "action": "login",
                "email": email,
                "result": "user_not_found",
                "ip": request.META.get("REMOTE_ADDR")
            }
        )
        return Response({"error": "E-mail ou senha incorretos."}, status=status.HTTP_404_NOT_FOUND)

    if user.check_password(request.data.get('password')):
        if not user.is_active:
            logger.warning(
                "Login failed: user inactive.",
                extra={
                    "action": "login",
                    "user_id": user.id,
                    "email": user.email,
                    "result": "inactive",
                    "ip": request.META.get("REMOTE_ADDR")
                }
            )
            return Response({"error": "Conta desativada."}, status=status.HTTP_403_FORBIDDEN)
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        refresh = RefreshToken.for_user(user)

        logger.info(
            "Login successful.",
            extra={
                "action": "login",
                "user_id": user.id,
                "email": user.email,
                "result": "success",
                "ip": request.META.get("REMOTE_ADDR")
            }
        )
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": GenericUserSerializer(user).data
        }, status=status.HTTP_200_OK)

    logger.warning(
        "Login failed: invalid password.",
        extra={
            "action": "login",
            "user_id": user.id,
            "email": user.email,
            "result": "invalid_password",
            "ip": request.META.get("REMOTE_ADDR")
        }
    )
    return Response({"error": "E-mail ou senha incorretos."}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_refresh_token(request):
    """
    View to obtain a new refresh token from loged in user.
    """
    user = request.user
    refresh_token = RefreshToken.for_user(user)

    return Response({
        "refresh": str(refresh_token)
    }, status=status.HTTP_200_OK)
