"""
Views for terms and conditions in the Natour API.
"""
# pylint: disable=no-member
import logging
import threading
from django.views.decorators.cache import cache_page
from django.db import transaction
from django_ratelimit.decorators import ratelimit

from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import permission_classes

from natour.api.models import Terms
from natour.api.serializers.terms import (CreateTermsSerializer, GetTermsSerializer,
                                          UpadateTermsSerializer)
from natour.api.methods.send_terms_email import send_updated_terms_email
from natour.api.schemas.terms_schemas import (
    create_terms_schema,
    get_terms_schema,
    update_terms_schema
)

from natour.api.utils.get_ip import get_client_ip

logger = logging.getLogger("django")


@create_terms_schema
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
@ratelimit(key='user', rate='5/h', block=True)
def create_terms(request):
    """
    Endpoint to create new terms and conditions.
    """
    user = request.user
    ip = get_client_ip(request)
    logger.info(
        "Admin '%s' (ID: %s, IP: %s) requested to create terms and conditions.",
        user.username, user.id, ip
    )

    if not request.data:
        return Response(
            {"detail": "Dados obrigatórios não fornecidos."},
            status=status.HTTP_400_BAD_REQUEST
        )

    with transaction.atomic():
        count = Terms.objects.select_for_update().count()
        logger.info(
            "Current Terms count before create attempt: %d.", count
        )

        if count >= 2:
            logger.warning(
                "Admin '%s' (ID: %s) attempted to create terms, but maximum count (%d) reached.",
                user.username, user.id, count
            )
            return Response(
                {"detail": "Termos e políticas já criados."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = CreateTermsSerializer(data=request.data)
        if serializer.is_valid():
            terms = serializer.save()
            logger.info(
                "Terms and conditions created by admin '%s' (ID: %s). Terms ID: %s, Title: '%s'.",
                user.username, user.id, terms.id, getattr(
                    terms, "title", "<no title>")
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        logger.warning(
            "Admin '%s' (ID: %s) failed to create terms and conditions due to validation errors: %s",
            user.username, user.id, serializer.errors
        )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@get_terms_schema
@cache_page(300)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_terms(request, term_id):
    """
    Endpoint to retrieve terms and conditions.
    """
    try:
        terms = Terms.objects.only(
            'id', 'title', 'content', 'created_at', 'updated_at').get(id=term_id)
        serializer = GetTermsSerializer(terms)

        logger.info(
            "Terms ID: %s retrieved successfully.",
            term_id
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Terms.DoesNotExist:
        logger.warning(
            "Attempted to retrieve non-existent Terms ID: %s.",
            term_id
        )
        return Response(
            {"detail": "Termos não encontrados."},
            status=status.HTTP_404_NOT_FOUND
        )


@update_terms_schema
@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsAdminUser])
@ratelimit(key='user', rate='10/h', block=True)
def update_terms(request, term_id):
    """
    Endpoint to update existing terms and conditions.
    """
    user = request.user
    ip = get_client_ip(request)
    logger.info(
        "Admin '%s' (ID: %s, IP: %s) requested to update Terms ID: %s.",
        user.username, user.id, ip, term_id
    )

    if not request.data:
        return Response(
            {"detail": "Dados obrigatórios não fornecidos."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if 'content' not in request.data:
        logger.warning(
            "Admin '%s' (ID: %s) attempted to update Terms ID: %s but 'content' field is missing.",
            user.username, user.id, term_id
        )
        return Response(
            {"detail": "Você deve fornecer o conteúdo dos termos."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        with transaction.atomic():
            terms = Terms.objects.select_for_update().get(id=term_id)
            old_content = terms.content

            serializer = UpadateTermsSerializer(
                terms, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                logger.info(
                    "Admin '%s' (ID: %s) successfully updated Terms ID: %s. Content changed from %d to %d characters.",
                    user.username, user.id, term_id, len(
                        old_content or ''), len(terms.content or '')
                )

                try:
                    logger.info(
                        "Triggering updated terms email notification for Terms ID: %s.", term_id
                    )
                    threading.Thread(
                        target=send_updated_terms_email, daemon=True).start()
                except Exception as e:
                    logger.error(
                        "Failed to start email notification thread for Terms ID: %s. Error: %s",
                        term_id, str(e)
                    )

                return Response(serializer.data, status=status.HTTP_200_OK)

            logger.warning(
                "Admin '%s' (ID: %s) failed to update Terms ID: %s due to validation errors: %s",
                user.username, user.id, term_id, serializer.errors
            )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Terms.DoesNotExist:
        logger.warning(
            "Admin '%s' (ID: %s) attempted to update non-existent Terms ID: %s.",
            user.username, user.id, term_id
        )
        return Response(
            {"detail": "Termos não encontrados."},
            status=status.HTTP_404_NOT_FOUND
        )
