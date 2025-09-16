"""
Schema definitions for Authentication views.
"""
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


# Login schema
login_schema = extend_schema(
    tags=['Authentication'],
    summary='User login',
    description='Authenticate user and return access/refresh tokens.',
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'email': {'type': 'string', 'format': 'email', 'description': 'User email'},
                'password': {'type': 'string', 'description': 'User password'},
                'remember_me': {'type': 'boolean', 'description': 'Extended token lifetime'}
            },
            'required': ['email', 'password']
        }
    },
    responses={
        200: OpenApiResponse(
            description='Login successful',
            examples=[
                OpenApiExample(
                    'Success',
                    value={
                        'access': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                        'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                        'user': {
                            'id': 1,
                            'username': 'Johnie',
                            'email': 'john@example.com',
                            'role': 'user'
                        },
                        'remember_me': False
                    }
                )
            ]
        ),
        400: OpenApiResponse(
            description='Invalid credentials',
            examples=[
                OpenApiExample(
                    'Invalid credentials',
                    value={'error': 'E-mail ou senha incorretos.'}
                )
            ]
        )
    }
)

# Create user schema
create_user_schema = extend_schema(
    tags=['Authentication'],
    summary='Register new user',
    description='Create a new user account.',
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'username': {'type': 'string', 'description': 'Unique username'},
                'email': {'type': 'string', 'format': 'email', 'description': 'User email'},
                'password': {'type': 'string', 'description': 'User password'}
            },
            'required': ['username', 'email', 'password']
        }
    },
    responses={
        201: OpenApiResponse(
            description='User created successfully',
            examples=[
                OpenApiExample(
                    'Success',
                    value={
                        'id': 1,
                        'username': 'newuser',
                        'email': 'user@example.com',
                        'role': 1
                    }
                )
            ]
        ),
        400: OpenApiResponse(
            description='Validation errors',
            examples=[
                OpenApiExample(
                    'Username exists',
                    value={'username': ['A user with that username already exists.']}
                ),
                OpenApiExample(
                    'Password validation error',
                    value={'password': ['Senha deve ter pelo menos 8 caracteres, incluindo letras e números.']}
                )
            ]
        )
    }
)

# Get refresh token schema
get_refresh_token_schema = extend_schema(
    tags=['Authentication'],
    summary='Get new refresh token',
    description='Get a new refresh token for the authenticated user.',
    request=None,
    responses={
        200: OpenApiResponse(
            description='Refresh token retrieved successfully',
            examples=[
                OpenApiExample(
                    'Success',
                    value={
                        'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                        'access': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'
                    }
                )
            ]
        ),
        403: OpenApiResponse(
            description='Account deactivated',
            examples=[
                OpenApiExample(
                    'Account inactive',
                    value={'detail': 'Conta desativada.'}
                )
            ]
        ),
        401: OpenApiResponse(description='Authentication required')
    }
)
