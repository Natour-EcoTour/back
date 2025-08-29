"""
Schema definitions for Terms views.
"""
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from drf_spectacular.openapi import OpenApiParameter

from natour.api.serializers.terms import CreateTermsSerializer, GetTermsSerializer, UpdateTermsSerializer


# Create terms schema
create_terms_schema = extend_schema(
    tags=['Terms'],
    summary='Create terms and conditions',
    description='Create new terms and conditions. Admin access required.',
    request=CreateTermsSerializer,
    responses={
        201: OpenApiResponse(
            response=GetTermsSerializer,
            description='Terms created successfully'
        ),
        400: OpenApiResponse(
            description='Validation errors',
            examples=[
                OpenApiExample(
                    'Missing content',
                    value={'content': ['This field is required.']}
                )
            ]
        ),
        403: OpenApiResponse(description='Admin access required'),
        401: OpenApiResponse(description='Authentication required')
    }
)

# Get terms schema
get_terms_schema = extend_schema(
    tags=['Terms'],
    summary='Get terms and conditions',
    description='Retrieve specific terms and conditions by ID.',
    parameters=[
        OpenApiParameter(
            name='term_id',
            type=int,
            location=OpenApiParameter.PATH,
            description='ID of the terms to retrieve'
        )
    ],
    responses={
        200: OpenApiResponse(
            response=GetTermsSerializer,
            description='Terms retrieved successfully'
        ),
        404: OpenApiResponse(
            description='Terms not found',
            examples=[
                OpenApiExample(
                    'Terms not found',
                    value={'detail': 'Termos não encontrados.'}
                )
            ]
        ),
        401: OpenApiResponse(description='Authentication required')
    }
)

# Update terms schema
update_terms_schema = extend_schema(
    tags=['Terms'],
    summary='Update terms and conditions',
    description='Update existing terms and conditions. Admin access required.',
    request=UpdateTermsSerializer,
    parameters=[
        OpenApiParameter(
            name='term_id',
            type=int,
            location=OpenApiParameter.PATH,
            description='ID of the terms to update'
        )
    ],
    responses={
        200: OpenApiResponse(
            response=GetTermsSerializer,
            description='Terms updated successfully'
        ),
        400: OpenApiResponse(
            description='Validation errors',
            examples=[
                OpenApiExample(
                    'Invalid data',
                    value={'content': ['This field may not be blank.']}
                )
            ]
        ),
        404: OpenApiResponse(
            description='Terms not found',
            examples=[
                OpenApiExample(
                    'Terms not found',
                    value={'detail': 'Termos não encontrados.'}
                )
            ]
        ),
        403: OpenApiResponse(description='Admin access required'),
        401: OpenApiResponse(description='Authentication required')
    }
)
