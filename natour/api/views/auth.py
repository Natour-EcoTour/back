"""
Views for user authentication and management.
"""
import logging

from smtplib import SMTPException

from django.conf import settings
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

from natour.api.serializers.user import CreateUserSerializer
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
    )

    if not cache.get(f'verified_email:{email}'):
        logger.warning(
            "User tried creating an account before code verification.",

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
            )
            return Response(
                {"detail": f"Erro ao enviar email: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        return Response(CreateUserSerializer(user).data, status=status.HTTP_201_CREATED)

    logger.warning(
        "User creation failed validation.",
    )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
@ratelimit(key='ip', rate='5/m', block=True)
def login(request):
    """
    Endpoint for user login with optional 'remember me' functionality.
    """
    email = request.data.get('email')
    remember_me = request.data.get('remember_me', False)  # Default to False

    logger.info(
        "Login attempt received.",
    )
    try:
        user = (CustomUser.objects
                .select_related('role')
                .only('id', 'email', 'password', 'is_active', 'last_login', 'role__name')
                .get(email=email))
    except ObjectDoesNotExist:
        logger.warning(
            "Login failed: user not found.",
        )
        return Response({"error": "E-mail ou senha incorretos."}, status=status.HTTP_404_NOT_FOUND)

    if user.check_password(request.data.get('password')):
        if not user.is_active:
            logger.warning(
                "Login failed: user inactive.",
            )
            return Response({"error": "Conta desativada."}, status=status.HTTP_403_FORBIDDEN)

        # user.last_login = timezone.now()
        # user.save(update_fields=['last_login'])

        refresh = RefreshToken.for_user(user)

        if remember_me:
            remember_me_settings = getattr(settings, 'REMEMBER_ME_JWT', {})
            access_lifetime = remember_me_settings.get('ACCESS_TOKEN_LIFETIME')
            refresh_lifetime = remember_me_settings.get(
                'REFRESH_TOKEN_LIFETIME')

            if access_lifetime:
                refresh.access_token.set_exp(lifetime=access_lifetime)
            if refresh_lifetime:
                refresh.set_exp(lifetime=refresh_lifetime)

        logger.info(
            "Login successful.",
        )
        return Response({
            "refresh": str(refresh),
            "access":  str(refresh.access_token),
            "user": {
                "id":       user.id,
                "username": user.username,
                "email":    user.email,
                "role":     user.role.name,
            },
            "remember_me": remember_me
        }, status=status.HTTP_200_OK)

    logger.warning(
        "Login failed: invalid password.",
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
