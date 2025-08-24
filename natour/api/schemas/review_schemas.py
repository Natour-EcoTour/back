"""
Schema definitions for Review views.
"""
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from drf_spectacular.openapi import OpenApiParameter

from natour.api.serializers.review import ReviewSerializer


# Add review schema
add_review_schema = extend_schema(
    tags=['Reviews'],
    summary='Add review to point',
    description='Add a review and rating to a tourism point.',
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'rating': {
                    'type': 'integer', 
                    'minimum': 1, 
                    'maximum': 5, 
                    'description': 'Rating from 1 to 5 stars'
                },
                'comment': {'type': 'string', 'description': 'Review comment (optional)'}
            },
            'required': ['rating']
        }
    },
    parameters=[
        OpenApiParameter(
            name='point_id',
            type=int,
            location=OpenApiParameter.PATH,
            description='ID of the point to review'
        )
    ],
    responses={
        201: OpenApiResponse(
            response=ReviewSerializer,
            description='Review added successfully'
        ),
        400: OpenApiResponse(
            description='Bad request - invalid rating or validation errors',
            examples=[
                OpenApiExample(
                    'Invalid rating',
                    value={'rating': ['Rating must be between 1 and 5.']}
                ),
                OpenApiExample(
                    'Already reviewed',
                    value={'detail': 'Você já avaliou este ponto.'}
                )
            ]
        ),
        404: OpenApiResponse(
            description='Point not found',
            examples=[
                OpenApiExample(
                    'Point not found',
                    value={'detail': 'Ponto não encontrado.'}
                )
            ]
        ),
        401: OpenApiResponse(description='Authentication required')
    }
)

# Get user reviews schema
get_user_reviews_schema = extend_schema(
    tags=['Reviews'],
    summary='Get user reviews',
    description='Retrieve reviews made by the authenticated user.',
    parameters=[
        OpenApiParameter(
            name='page',
            type=int,
            location=OpenApiParameter.QUERY,
            description='Page number for pagination'
        ),
        OpenApiParameter(
            name='page_size',
            type=int,
            location=OpenApiParameter.QUERY,
            description='Number of items per page'
        )
    ],
    responses={
        200: OpenApiResponse(
            response=ReviewSerializer,
            description='User reviews retrieved successfully'
        ),
        401: OpenApiResponse(description='Authentication required')
    }
)
