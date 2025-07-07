"""
Views for managing verification codes in the Natour API.
"""
# pylint: disable=no-member
import logging

from smtplib import SMTPException

from django.core.cache import cache
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django_ratelimit.decorators import ratelimit
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework import status
from rest_framework.decorators import permission_classes

from natour.api.methods.create_code import create_code
from natour.api.models import CustomUser
from natour.api.serializers.user import NewUserPasswordSerializer

logger = logging.getLogger("django")


@api_view(['POST'])
@permission_classes([AllowAny])
@ratelimit(key='ip', rate='5/m', block=True)
def send_verification_code(request):
    """
    View to send a verification code to a user's email.
    """
    target_username = request.data.get('username')
    target_email = request.data.get('email')

    logger.info(
        "Verification code request received.",
        extra={
            "action": "send_verification_code",
            "username": target_username,
            "email": target_email,
            "ip": request.META.get("REMOTE_ADDR")
        }
    )

    if not target_email or not target_username:
        logger.warning(
            "Verification code request missing email or username.",
            extra={
                "action": "send_verification_code",
                "username": target_username,
                "email": target_email,
                "result": "missing_fields",
                "ip": request.META.get("REMOTE_ADDR")
            }
        )
        return Response({"detail": "Forneça um nome e e-mail."}, status=status.HTTP_400_BAD_REQUEST)

    cache_key = f'verification_code:{target_email}'
    if cache.get(cache_key):
        logger.warning(
            "Verification code request too soon.",
            extra={
                "action": "send_verification_code",
                "username": target_username,
                "email": target_email,
                "result": "rate_limited",
                "ip": request.META.get("REMOTE_ADDR")
            }
        )
        return Response(
            {"detail": "Por favor espere 3 minutos para solicitar outro código."},
            status=status.HTTP_400_BAD_REQUEST
        )

    code = create_code()
    cache.set(cache_key, code, timeout=180)

    logger.info(
        "Verification code generated and cached.",
        extra={
            "action": "send_verification_code",
            "username": target_username,
            "email": target_email,
            "code": code,
            "result": "code_generated",
            "ip": request.META.get("REMOTE_ADDR")
        }
    )

    html_content = render_to_string(
        'email_templates/validation_code.html',
        {
            'username': target_username,
            'verification_code': code
        }
    )

    try:
        msg = EmailMultiAlternatives(
            subject="Natour - Status da Conta",
            body="Código de verificação para sua conta Natour",
            from_email="natourproject@gmail.com",
            to=[target_email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
    except SMTPException as e:
        logger.error(
            "Failed to send verification code email.",
            extra={
                "action": "send_verification_code",
                "username": target_username,
                "email": target_email,
                "code": code,
                "result": "email_send_failed",
                "error": str(e),
                "ip": request.META.get("REMOTE_ADDR")
            }
        )
        return Response(
            {"detail": f"Erro ao enviar email: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    logger.info(
        "Verification code email sent successfully.",
        extra={
            "action": "send_verification_code",
            "username": target_username,
            "email": target_email,
            "code": code,
            "result": "success",
            "ip": request.META.get("REMOTE_ADDR")
        }
    )

    return Response({
        "detail": "Código de verificação enviado com sucesso. Verifique seu e-mail.",
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_code(request):
    """
    View to verify the code sent to the user's email.
    """
    email = request.data.get('email')
    code = request.data.get('code')

    logger.info(
        "Verification code submission received.",
        extra={
            "action": "verify_code",
            "email": email,
            "ip": request.META.get("REMOTE_ADDR")
        }
    )

    cache_key = f'verification_code:{email}'
    cached_code = cache.get(cache_key)

    if not cached_code:
        logger.warning(
            "Verification code failed: expired or not found.",
            extra={
                "action": "verify_code",
                "email": email,
                "result": "expired_or_not_found",
                "ip": request.META.get("REMOTE_ADDR")
            }
        )
        return Response({"detail": "Código expirado ou não encontrado."},
                        status=status.HTTP_400_BAD_REQUEST)

    if cached_code != code:
        logger.warning(
            "Verification code failed: incorrect code.",
            extra={
                "action": "verify_code",
                "email": email,
                "result": "incorrect_code",
                "ip": request.META.get("REMOTE_ADDR")
            }
        )
        return Response({"detail": "Código incorreto."}, status=status.HTTP_400_BAD_REQUEST)

    cache.delete(cache_key)
    cache.set(f'verified_email:{email}', True, timeout=600)

    logger.info(
        "Verification code successful: email verified.",
        extra={
            "action": "verify_code",
            "email": email,
            "result": "success",
            "ip": request.META.get("REMOTE_ADDR")
        }
    )

    return Response({"detail": "Email verificado com sucesso!"}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def send_password_reset_code(request):
    """
    View to send a password reset code to the user's email.
    """
    target_email = request.data.get('email')

    if not target_email:
        return Response({"detail": "Forneça um nome e e-mail."}, status=status.HTTP_400_BAD_REQUEST)

    cache_key = f'verification_code:{target_email}'
    code = create_code()
    cache.set(cache_key, code, timeout=180)

    html_content = render_to_string(
        'email_templates/password_code_request.html',
        {
            'verification_code': code
        }
    )

    try:
        msg = EmailMultiAlternatives(
            subject="Natour - Redefinição de Senha",
            body="Código de verificação para redefinição de senha",
            from_email="natourproject@gmail.com",
            to=[target_email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return Response(
            {"detail": "Código de redefinição de senha enviado com sucesso."},
            status=status.HTTP_200_OK
        )
    except SMTPException as e:
        return Response(
            {"detail": f"Erro ao enviar email: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_password_reset_code(request):
    """
    View to verify the password reset code sent to the user's email.
    """
    user = get_object_or_404(CustomUser, email=request.data.get('email'))

    email = request.data.get('email')
    code = request.data.get('code')

    if not email or not code:
        return Response({"detail": "E-mail e código são obrigatórios."},
                        status=status.HTTP_400_BAD_REQUEST)

    cache_key = f'verification_code:{email}'
    cached_code = cache.get(cache_key)

    if not cached_code:
        return Response({"detail": "Código expirado ou não encontrado."},
                        status=status.HTTP_400_BAD_REQUEST)

    if cached_code != code:
        return Response({"detail": "Código incorreto."}, status=status.HTTP_400_BAD_REQUEST)

    serializer = NewUserPasswordSerializer(data=request.data)
    if serializer.is_valid():
        user.set_password(serializer.validated_data['password'])
        user.save()

        cache.delete(cache_key)
        cache.set(f'password_reset_verified:{email}', True, timeout=600)

        return Response(
            {"detail": "Senha atualizada com sucesso."},
            status=status.HTTP_200_OK
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
