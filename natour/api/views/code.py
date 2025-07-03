"""
Views for managing verification codes in the Natour API.
"""
# pylint: disable=no-member

from smtplib import SMTPException

from django.core.cache import cache
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django_ratelimit.decorators import ratelimit
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import permission_classes

from natour.api.methods.create_code import create_code


@api_view(['POST'])
@permission_classes([AllowAny])
@ratelimit(key='ip', rate='5/m', block=True)
def send_verification_code(request):
    """
    View to send a verification code to a user's email.
    """
    target_username = request.data.get('username')
    target_email = request.data.get('email')

    if not target_email or not target_username:
        return Response({"detail": "Forneça um nome e e-mail."}, status=status.HTTP_400_BAD_REQUEST)

    cache_key = f'verification_code:{target_email}'
    if cache.get(cache_key):
        return Response(
            {"detail": "Por favor espere 3 minutos para solicitar outro código."},
            status=status.HTTP_400_BAD_REQUEST
        )

    code = create_code()
    cache.set(cache_key, code, timeout=180)

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
        return Response(
            {"detail": f"Erro ao enviar email: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
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

    cache_key = f'verification_code:{email}'
    cached_code = cache.get(cache_key)

    if not cached_code:
        return Response({"detail": "Código expirado ou não encontrado."},
                        status=status.HTTP_400_BAD_REQUEST)
    if cached_code != code:
        return Response({"detail": "Código incorreto."}, status=status.HTTP_400_BAD_REQUEST)

    cache.delete(cache_key)

    cache.set(f'verified_email:{email}', True, timeout=600)

    return Response({"detail": "Email verificado com sucesso!"}, status=status.HTTP_200_OK)
