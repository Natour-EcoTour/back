"""
Views for user authentication and management.
"""

from smtplib import SMTPException

from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

from django_ratelimit.decorators import ratelimit

from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from natour.api.serializers.user import CreateUserSerializer, GenericUserSerializer
from natour.api.models import CustomUser


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
    serializer = CreateUserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()

        if user.role and user.role.name == 'master':
            user.is_staff = True
            user.is_superuser = True
            user.save(update_fields=['is_staff', 'is_superuser'])

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
            return Response(
                {"detail": f"Erro ao enviar email: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        return Response(CreateUserSerializer(user).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
@ratelimit(key='ip', rate='5/m', block=True)
def login(request):
    """
    Endpoint for user login.
    """
    try:
        user = CustomUser.objects.get(email=request.data['email'])
    except CustomUser.DoesNotExist:  # pylint: disable=no-member
        return Response({"error": "E-mail ou senha incorretos."}, status=status.HTTP_404_NOT_FOUND)

    if user.check_password(request.data['password']):
        if user.is_active is False:
            return Response({"error": "Conta desativada."}, status=status.HTTP_403_FORBIDDEN)
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": GenericUserSerializer(user).data
        }, status=status.HTTP_200_OK)

    return Response({"error": "E-mail ou senha incorretos."}, status=status.HTTP_401_UNAUTHORIZED)

# logout
