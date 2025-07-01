"""
Views for terms and conditions in the Natour API.
"""

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
from natour.api.tasks import send_updated_terms_email


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def create_terms(request):
    """
    Endpoint to create new terms and conditions.
    """
    count = Terms.objects.count()  # pylint: disable=no-member

    if count >= 2:
        return Response(
            {"detail": "Termos e políticas já criados."},
            status=status.HTTP_400_BAD_REQUEST)

    serializer = CreateTermsSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
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
    if 'content' not in request.data:
        return Response(
            {"detail": "Você deve fornecer o conteúdo dos termos."},
            status=status.HTTP_400_BAD_REQUEST
        )

    terms = get_object_or_404(Terms, id=term_id)
    serializer = UpadateTermsSerializer(terms, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        threading.Thread(target=send_updated_terms_email, daemon=True).start()
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
