"""
Views for terms and conditions in the Natour API.
"""
# pylint: disable=no-member
import logging
import threading
from django.views.decorators.cache import cache_page

from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.generics import get_object_or_404


from natour.api.models import Terms
from natour.api.serializers.terms import (CreateTermsSerializer, GetTermsSerializer,
                                          UpadateTermsSerializer)
from natour.api.methods.send_terms_email import send_updated_terms_email

from natour.api.utils.get_ip import get_client_ip

logger = logging.getLogger("django")


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
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

    count = Terms.objects.count()
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


@cache_page(60)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_terms(request, term_id):
    """
    Endpoint to retrieve terms and conditions.
    """
    terms = get_object_or_404(Terms, id=term_id)
    serializer = GetTermsSerializer(terms)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsAdminUser])
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

    if 'content' not in request.data:
        logger.warning(
            "Admin '%s' (ID: %s) attempted to update Terms ID: %s but 'content' field is missing.",
            user.username, user.id, term_id
        )
        return Response(
            {"detail": "Você deve fornecer o conteúdo dos termos."},
            status=status.HTTP_400_BAD_REQUEST
        )

    terms = get_object_or_404(Terms, id=term_id)
    serializer = UpadateTermsSerializer(terms, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        logger.info(
            "Admin '%s' (ID: %s) successfully updated Terms ID: %s.",
            user.username, user.id, term_id
        )
        logger.info(
            "Triggering updated terms email notification for Terms ID: %s.", term_id
        )
        threading.Thread(target=send_updated_terms_email, daemon=True).start()
        return Response(serializer.data, status=status.HTTP_200_OK)

    logger.warning(
        "Admin '%s' (ID: %s) failed to update Terms ID: %s due to validation errors: %s",
        user.username, user.id, term_id, serializer.errors
    )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
