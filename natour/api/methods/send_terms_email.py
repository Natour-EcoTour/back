"""
Module for sending emails to users when terms and policies are updated.
"""
from smtplib import SMTPException

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model


def send_updated_terms_email():
    """
    Sends an email to all active users notifying them of updated terms and policies.
    """
    CustomUser = get_user_model()
    users = CustomUser.objects.filter(is_active=True)
    for user in users:
        html_content = render_to_string(
            'email_templates/updated_terms.html',
            {'username': user.username}
        )
        try:
            msg = EmailMultiAlternatives(
                subject="Natour - Atualização dos Termos e Políticas",
                body=f"Olá, {user.username}! Os termos e políticas do Natour foram atualizados. Por favor, verifique seu email para mais detalhes.",
                from_email="natourproject@gmail.com",
                to=[user.email],
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        except SMTPException as e:
            # You might want to log this, but don't return a response from here
            print(f"Erro ao enviar email para {user.email}: {str(e)}")
