"""
Schema definitions for Photo views.
"""
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from drf_spectacular.openapi import OpenApiParameter

from natour.api.serializers.photo import PhotoSerializer


# Create photo schema
create_photo_schema = extend_schema(
    tags=['Photos'],
    summary='Upload photo',
    description='Upload a photo for a user or point.',
    request={
        'multipart/form-data': {
            'type': 'object',
            'properties': {
                'image': {'type': 'string', 'format': 'binary', 'description': 'Image file to upload'},
                'description': {'type': 'string', 'description': 'Photo description (optional)'}
            },
            'required': ['image']
        }
    },
    parameters=[
        OpenApiParameter(
            name='user_id',
            type=int,
            location=OpenApiParameter.PATH,
            description='ID of the user (for user photos)',
            required=False
        ),
        OpenApiParameter(
            name='point_id',
            type=int,
            location=OpenApiParameter.PATH,
            description='ID of the point (for point photos)',
            required=False
        )
    ],
    responses={
        201: OpenApiResponse(
            response=PhotoSerializer,
            description='Photo uploaded successfully'
        ),
        400: OpenApiResponse(
            description='Bad request - invalid file or validation errors',
            examples=[
                OpenApiExample(
                    'Invalid file type',
                    value={'detail': 'Formato de arquivo não suportado.'}
                )
            ]
        ),
        401: OpenApiResponse(description='Authentication required'),
        403: OpenApiResponse(description='Permission denied')
    }
)

# Update photo schema
update_photo_schema = extend_schema(
    tags=['Photos'],
    summary='Update photo',
    description='Update photo information or replace the image.',
    request={
        'multipart/form-data': {
            'type': 'object',
            'properties': {
                'image': {'type': 'string', 'format': 'binary', 'description': 'New image file (optional)'},
                'description': {'type': 'string', 'description': 'Photo description'}
            }
        }
    },
    parameters=[
        OpenApiParameter(
            name='photo_id',
            type=int,
            location=OpenApiParameter.PATH,
            description='ID of the photo to update'
        )
    ],
    responses={
        200: OpenApiResponse(
            response=PhotoSerializer,
            description='Photo updated successfully'
        ),
        404: OpenApiResponse(
            description='Photo not found',
            examples=[
                OpenApiExample(
                    'Photo not found',
                    value={'detail': 'Foto não encontrada.'}
                )
            ]
        ),
        401: OpenApiResponse(description='Authentication required'),
        403: OpenApiResponse(description='Permission denied')
    }
)

# Get photos schema
get_photo_schema = extend_schema(
    tags=['Photos'],
    summary='List photos',
    description='Retrieve a list of photos with optional filtering.',
    parameters=[
        OpenApiParameter(
            name='user_id',
            type=int,
            location=OpenApiParameter.QUERY,
            description='Filter by user ID',
            required=False
        ),
        OpenApiParameter(
            name='point_id',
            type=int,
            location=OpenApiParameter.QUERY,
            description='Filter by point ID',
            required=False
        ),
        OpenApiParameter(
            name='page',
            type=int,
            location=OpenApiParameter.QUERY,
            description='Page number for pagination'
        )
    ],
    responses={
        200: OpenApiResponse(
            response=PhotoSerializer,
            description='Photos retrieved successfully'
        ),
        401: OpenApiResponse(description='Authentication required')
    }
)

# Delete photo schema
delete_photo_schema = extend_schema(
    tags=['Photos'],
    summary='Delete photo',
    description='Delete a photo by ID.',
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'photo_id': {'type': 'integer', 'description': 'ID of the photo to delete'}
            },
            'required': ['photo_id']
        }
    },
    responses={
        204: OpenApiResponse(description='Photo deleted successfully'),
        404: OpenApiResponse(
            description='Photo not found',
            examples=[
                OpenApiExample(
                    'Photo not found',
                    value={'detail': 'Foto não encontrada.'}
                )
            ]
        ),
        401: OpenApiResponse(description='Authentication required'),
        403: OpenApiResponse(description='Permission denied')
    }
)
