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

logger = logging.getLogger("django")


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def create_terms(request):
    """
    Endpoint to create new terms and conditions.
    """
    user = request.user
    logger.info(
        "Received request to create terms and conditions.",
        extra={
            "action": "create_terms",
            "user_id": user.id,
            "username": user.username,
            "ip": request.META.get("REMOTE_ADDR")
        }
    )

    count = Terms.objects.count()
    if count >= 2:
        logger.warning(
            "Attempt to create terms when already at maximum count.",
            extra={
                "action": "create_terms",
                "user_id": user.id,
                "username": user.username,
                "count": count,
                "result": "max_terms_reached",
                "ip": request.META.get("REMOTE_ADDR")
            }
        )
        return Response(
            {"detail": "Termos e políticas já criados."},
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer = CreateTermsSerializer(data=request.data)
    if serializer.is_valid():
        terms = serializer.save()
        logger.info(
            "Terms and conditions created successfully.",
            extra={
                "action": "create_terms",
                "user_id": user.id,
                "username": user.username,
                "terms_id": terms.id,
                "result": "success",
                "ip": request.META.get("REMOTE_ADDR")
            }
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    logger.warning(
        "Failed to create terms and conditions due to validation errors.",
        extra={
            "action": "create_terms",
            "user_id": user.id,
            "username": user.username,
            "errors": serializer.errors,
            "result": "validation_error",
            "ip": request.META.get("REMOTE_ADDR")
        }
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
    logger.info(
        "Received request to update terms and conditions.",
        extra={
            "action": "update_terms",
            "user_id": user.id,
            "username": user.username,
            "term_id": term_id,
            "ip": request.META.get("REMOTE_ADDR")
        }
    )

    if 'content' not in request.data:
        logger.warning(
            "Update terms request missing content field.",
            extra={
                "action": "update_terms",
                "user_id": user.id,
                "username": user.username,
                "term_id": term_id,
                "result": "missing_content",
                "ip": request.META.get("REMOTE_ADDR")
            }
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
            "Terms and conditions updated successfully.",
            extra={
                "action": "update_terms",
                "user_id": user.id,
                "username": user.username,
                "term_id": term_id,
                "result": "success",
                "ip": request.META.get("REMOTE_ADDR")
            }
        )
        # Email send runs in background; log its dispatch.
        logger.info(
            "Dispatched email notification for updated terms.",
            extra={
                "action": "update_terms_email",
                "user_id": user.id,
                "username": user.username,
                "term_id": term_id,
                "ip": request.META.get("REMOTE_ADDR")
            }
        )
        threading.Thread(target=send_updated_terms_email, daemon=True).start()
        return Response(serializer.data, status=status.HTTP_200_OK)

    logger.warning(
        "Failed to update terms and conditions due to validation errors.",
        extra={
            "action": "update_terms",
            "user_id": user.id,
            "username": user.username,
            "term_id": term_id,
            "errors": serializer.errors,
            "result": "validation_error",
            "ip": request.META.get("REMOTE_ADDR")
        }
    )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
