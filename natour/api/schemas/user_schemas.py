"""
Schema definitions for User views.
"""
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from drf_spectacular.openapi import OpenApiParameter

from natour.api.serializers.user import (
    CustomUserInfoSerializer,
    UpdateUserSerializer,
    AllUsersSerializer,
    UserStatusSerializer,
    UserPasswordSerializer
)


# Get my info schema
get_my_info_schema = extend_schema(
    tags=['Users'],
    summary='Get current user information',
    description='Retrieve information about the currently authenticated user.',
    responses={
        200: OpenApiResponse(
            response=CustomUserInfoSerializer,
            description='User information retrieved successfully'
        ),
        401: OpenApiResponse(description='Authentication required')
    }
)

# Update my info schema
update_my_info_schema = extend_schema(
    tags=['Users'],
    summary='Update current user information',
    description='Update profile information for the currently authenticated user.',
    request=UpdateUserSerializer,
    responses={
        200: OpenApiResponse(
            response=CustomUserInfoSerializer,
            description='User information updated successfully'
        ),
        400: OpenApiResponse(
            description='Validation errors',
            examples=[
                OpenApiExample(
                    'Invalid email',
                    value={'email': ['Enter a valid email address.']}
                )
            ]
        ),
        401: OpenApiResponse(description='Authentication required')
    }
)

# Get all users schema (Admin only)
get_all_users_schema = extend_schema(
    tags=['Users'],
    summary='List all users',
    description='Retrieve a paginated list of all users. Admin access required.',
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
            response=AllUsersSerializer,
            description='Users retrieved successfully'
        ),
        403: OpenApiResponse(description='Admin access required'),
        401: OpenApiResponse(description='Authentication required')
    }
)

# Change user status schema (Admin only)
change_user_status_schema = extend_schema(
    tags=['Users'],
    summary='Change user status',
    description='Activate or deactivate a user account. Admin access required.',
    request=UserStatusSerializer,
    parameters=[
        OpenApiParameter(
            name='user_id',
            type=int,
            location=OpenApiParameter.PATH,
            description='ID of the user to update'
        )
    ],
    responses={
        200: OpenApiResponse(
            response=UserStatusSerializer,
            description='User status updated successfully'
        ),
        403: OpenApiResponse(description='Admin access required'),
        404: OpenApiResponse(
            description='User not found',
            examples=[
                OpenApiExample(
                    'User not found',
                    value={'detail': 'Usuário não encontrado.'}
                )
            ]
        ),
        401: OpenApiResponse(description='Authentication required')
    }
)

# Update password schema
update_my_password_schema = extend_schema(
    tags=['Users'],
    summary='Update current user password',
    description='Change password for the currently authenticated user.',
    request=UserPasswordSerializer,
    responses={
        200: OpenApiResponse(
            description='Password updated successfully',
            examples=[
                OpenApiExample(
                    'Success',
                    value={'detail': 'Senha atualizada com sucesso.'}
                )
            ]
        ),
        400: OpenApiResponse(
            description='Validation errors',
            examples=[
                OpenApiExample(
                    'Weak password',
                    value={'password': ['This password is too common.']}
                )
            ]
        ),
        401: OpenApiResponse(description='Authentication required')
    }
)

# Delete user account schema
delete_my_account_schema = extend_schema(
    tags=['Users'],
    summary='Delete current user account',
    description='Permanently delete the currently authenticated user account.',
    responses={
        204: OpenApiResponse(description='Account deleted successfully'),
        401: OpenApiResponse(description='Authentication required')
    }
)

# Delete user account by admin schema
delete_user_account_schema = extend_schema(
    tags=['Users'],
    summary='Delete user account (Admin)',
    description='Delete a user account by ID. Admin access required.',
    parameters=[
        OpenApiParameter(
            name='user_id',
            type=int,
            location=OpenApiParameter.PATH,
            description='ID of the user to delete'
        )
    ],
    responses={
        204: OpenApiResponse(description='User account deleted successfully'),
        404: OpenApiResponse(
            description='User not found',
            examples=[
                OpenApiExample(
                    'User not found',
                    value={'detail': 'Usuário não encontrado.'}
                )
            ]
        ),
        403: OpenApiResponse(description='Admin access required'),
        401: OpenApiResponse(description='Authentication required')
    }
)

# Get user points schema
get_user_points_schema = extend_schema(
    tags=['Users'],
    summary='Get user points',
    description='Retrieve points created by a specific user.',
    parameters=[
        OpenApiParameter(
            name='user_id',
            type=int,
            location=OpenApiParameter.PATH,
            description='ID of the user'
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
            description='User points retrieved successfully'
        ),
        404: OpenApiResponse(
            description='User not found',
            examples=[
                OpenApiExample(
                    'User not found',
                    value={'detail': 'Usuário não encontrado.'}
                )
            ]
        ),
        401: OpenApiResponse(description='Authentication required')
    }
)

# Get my points schema
get_my_points_schema = extend_schema(
    tags=['Users'],
    summary='Get current user points',
    description='Retrieve points created by the authenticated user.',
    parameters=[
        OpenApiParameter(
            name='page',
            type=int,
            location=OpenApiParameter.QUERY,
            description='Page number for pagination'
        )
    ],
    responses={
        200: OpenApiResponse(
            description='User points retrieved successfully'
        ),
        401: OpenApiResponse(description='Authentication required')
    }
)

# Reset user password schema
reset_user_password_schema = extend_schema(
    tags=['Users'],
    summary='Reset user password (Admin)',
    description='Reset password for a specific user. Admin access required.',
    parameters=[
        OpenApiParameter(
            name='user_id',
            type=int,
            location=OpenApiParameter.PATH,
            description='ID of the user'
        )
    ],
    request=None,
    responses={
        200: OpenApiResponse(
            description='Password reset successfully',
            examples=[
                OpenApiExample(
                    'Success',
                    value={'detail': 'Senha redefinida com sucesso.'}
                )
            ]
        ),
        404: OpenApiResponse(
            description='User not found',
            examples=[
                OpenApiExample(
                    'User not found',
                    value={'detail': 'No CustomUser matches the given query.'}
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
        403: OpenApiResponse(description='Admin access required'),
        401: OpenApiResponse(description='Authentication required')
    }
)
