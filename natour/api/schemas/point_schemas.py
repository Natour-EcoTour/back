"""
Schema definitions for Point views.
"""
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from drf_spectacular.openapi import OpenApiParameter

from natour.api.serializers.point import (
    CreatePointSerializer, 
    PointInfoSerializer,
    PointOnMapSerializer,
    PointApprovalSerializer,
    PointStatusUser,
    PointMapSearchSerializer
)


# Point creation schema
create_point_schema = extend_schema(
    tags=['Points'],
    summary='Create a new tourism point',
    description='Create a new point of interest for eco-tourism. Requires authentication.',
    request=CreatePointSerializer,
    responses={
        201: OpenApiResponse(
            response=CreatePointSerializer,
            description='Point created successfully'
        ),
        400: OpenApiResponse(
            description='Bad request - validation errors or missing required data',
            examples=[
                OpenApiExample(
                    'Missing data',
                    value={'detail': 'Dados obrigatórios não fornecidos.'}
                ),
                OpenApiExample(
                    'Validation error',
                    value={'name': ['This field is required.']}
                )
            ]
        ),
        401: OpenApiResponse(description='Authentication required')
    }
)

# Get point info schema
get_point_info_schema = extend_schema(
    operation_id='get_point_by_id',
    tags=['Points'],
    summary='Get point information',
    description='Retrieve detailed information about a specific tourism point.',
    parameters=[
        OpenApiParameter(
            name='point_id',
            type=int,
            location=OpenApiParameter.PATH,
            description='ID of the point to retrieve'
        )
    ],
    responses={
        200: OpenApiResponse(
            response=PointInfoSerializer,
            description='Point information retrieved successfully'
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

# Get all points schema
get_all_points_schema = extend_schema(
    operation_id='list_all_points',
    tags=['Points'],
    summary='List all points',
    description='Retrieve a paginated list of all tourism points.',
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
            response=PointInfoSerializer,
            description='Points retrieved successfully'
        ),
        401: OpenApiResponse(description='Authentication required')
    }
)

# Show points on map schema
show_points_on_map_schema = extend_schema(
    tags=['Points'],
    summary='Get points for map display',
    description='Get all points to display on the map with simplified data.',
    responses={
        200: OpenApiResponse(
            response=PointOnMapSerializer,
            description='Map points retrieved successfully'
        ),
        401: OpenApiResponse(description='Authentication required')
    }
)

# Point approval schema
point_approval_schema = extend_schema(
    tags=['Points'],
    summary='Approve or reject a point',
    description='Admin function to approve or reject a submitted point.',
    request=PointApprovalSerializer,
    parameters=[
        OpenApiParameter(
            name='point_id',
            type=int,
            location=OpenApiParameter.PATH,
            description='ID of the point to approve/reject'
        )
    ],
    responses={
        200: OpenApiResponse(
            response=PointApprovalSerializer,
            description='Point approval status updated successfully'
        ),
        403: OpenApiResponse(description='Admin access required'),
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

# Search points schema
search_point_schema = extend_schema(
    tags=['Points'],
    summary='Search points by name',
    description='Search for tourism points by name. Requires authentication.',
    parameters=[
        OpenApiParameter(
            name='name',
            type=str,
            location=OpenApiParameter.QUERY,
            description='Point name to search for (minimum 2 characters)',
            required=True
        )
    ],
    responses={
        200: OpenApiResponse(
            response=PointMapSearchSerializer(many=True),
            description='Search results retrieved successfully'
        ),
        400: OpenApiResponse(
            description='Bad request - missing or invalid search parameters',
            examples=[
                OpenApiExample(
                    'Missing name parameter',
                    value={'detail': "Parâmetro 'name' é obrigatório para a busca."}
                ),
                OpenApiExample(
                    'Name too short',
                    value={'detail': 'Nome deve ter pelo menos 2 caracteres.'}
                )
            ]
        ),
        404: OpenApiResponse(
            description='No points found',
            examples=[
                OpenApiExample(
                    'No results',
                    value={'detail': 'Nenhum ponto encontrado.'}
                )
            ]
        ),
        401: OpenApiResponse(description='Authentication required')
    }
)

# Change point status schema
change_point_status_schema = extend_schema(
    tags=['Points'],
    summary='Change point status',
    description='Toggle the active status of a point. Only the point creator can change its status.',
    parameters=[
        OpenApiParameter(
            name='point_id',
            type=int,
            location=OpenApiParameter.PATH,
            description='ID of the point to change status'
        )
    ],
    request=PointStatusUser,
    responses={
        200: OpenApiResponse(
            response=PointStatusUser,
            description='Point status changed successfully'
        ),
        400: OpenApiResponse(
            description='Validation errors',
            examples=[
                OpenApiExample(
                    'Validation error',
                    value={'field': ['This field is required.']}
                )
            ]
        ),
        404: OpenApiResponse(
            description='Point not found',
            examples=[
                OpenApiExample(
                    'Point not found',
                    value={'detail': 'No Point matches the given query.'}
                )
            ]
        ),
        401: OpenApiResponse(description='Authentication required')
    }
)

# Delete point (admin) schema
delete_point_schema = extend_schema(
    tags=['Points'],
    summary='Delete point (Admin)',
    description='Delete a point (admin access required). Sends notification email to the point creator.',
    parameters=[
        OpenApiParameter(
            name='point_id',
            type=int,
            location=OpenApiParameter.PATH,
            description='ID of the point to delete'
        )
    ],
    responses={
        204: OpenApiResponse(description='Point deleted successfully'),
        404: OpenApiResponse(
            description='Point not found',
            examples=[
                OpenApiExample(
                    'Point not found',
                    value={'detail': 'No Point matches the given query.'}
                )
            ]
        ),
        500: OpenApiResponse(
            description='Email sending error',
            examples=[
                OpenApiExample(
                    'Email error',
                    value={'detail': 'Erro ao enviar email: SMTP error'}
                )
            ]
        ),
        401: OpenApiResponse(description='Authentication required'),
        403: OpenApiResponse(description='Admin access required')
    }
)

# Delete my point schema
delete_my_point_schema = extend_schema(
    tags=['Points'],
    summary='Delete my point',
    description='Delete a point created by the authenticated user.',
    parameters=[
        OpenApiParameter(
            name='point_id',
            type=int,
            location=OpenApiParameter.PATH,
            description='ID of the point to delete'
        )
    ],
    responses={
        204: OpenApiResponse(description='Point deleted successfully'),
        404: OpenApiResponse(
            description='Point not found or unauthorized',
            examples=[
                OpenApiExample(
                    'Point not found',
                    value={'detail': 'No Point matches the given query.'}
                )
            ]
        ),
        401: OpenApiResponse(description='Authentication required')
    }
)

# Add view schema
add_view_schema = extend_schema(
    tags=['Points'],
    summary='Increment point view count',
    description='Increment the view count of a specific point.',
    parameters=[
        OpenApiParameter(
            name='point_id',
            type=int,
            location=OpenApiParameter.PATH,
            description='ID of the point to increment views'
        )
    ],
    request=None,
    responses={
        200: OpenApiResponse(
            description='View count incremented successfully',
            examples=[
                OpenApiExample(
                    'Success response',
                    value={'views': 42}
                )
            ]
        ),
        404: OpenApiResponse(
            description='Point not found',
            examples=[
                OpenApiExample(
                    'Point not found',
                    value={'detail': 'No Point matches the given query.'}
                )
            ]
        ),
        401: OpenApiResponse(description='Authentication required')
    }
)

# Edit point schema
edit_point_schema = extend_schema(
    tags=['Points'],
    summary='Edit point',
    description='Edit a point created by the authenticated user.',
    parameters=[
        OpenApiParameter(
            name='point_id',
            type=int,
            location=OpenApiParameter.PATH,
            description='ID of the point to edit'
        )
    ],
    request=CreatePointSerializer,
    responses={
        200: OpenApiResponse(
            response=CreatePointSerializer,
            description='Point updated successfully'
        ),
        400: OpenApiResponse(
            description='Bad request - validation errors or missing data',
            examples=[
                OpenApiExample(
                    'Missing data',
                    value={'detail': 'Dados obrigatórios não fornecidos.'}
                ),
                OpenApiExample(
                    'Validation error',
                    value={'name': ['This field is required.']}
                )
            ]
        ),
        404: OpenApiResponse(
            description='Point not found or unauthorized',
            examples=[
                OpenApiExample(
                    'Point not found',
                    value={'detail': 'Ponto não encontrado ou você não tem permissão para editá-lo.'}
                )
            ]
        ),
        401: OpenApiResponse(description='Authentication required')
    }
)
