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
                'username': {'type': 'string', 'description': 'Username or email'},
                'password': {'type': 'string', 'description': 'User password'},
                'remember_me': {'type': 'boolean', 'description': 'Extended token lifetime'}
            },
            'required': ['username', 'password']
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
                            'username': 'johndoe',
                            'email': 'john@example.com'
                        }
                    }
                )
            ]
        ),
        400: OpenApiResponse(
            description='Invalid credentials',
            examples=[
                OpenApiExample(
                    'Invalid credentials',
                    value={'detail': 'Credenciais inválidas.'}
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
                'password': {'type': 'string', 'description': 'User password'},
                'password_confirm': {'type': 'string', 'description': 'Password confirmation'},
                'first_name': {'type': 'string', 'description': 'First name'},
                'last_name': {'type': 'string', 'description': 'Last name'}
            },
            'required': ['username', 'email', 'password', 'password_confirm']
        }
    },
    responses={
        201: OpenApiResponse(
            description='User created successfully',
            examples=[
                OpenApiExample(
                    'Success',
                    value={
                        'detail': 'Usuário criado com sucesso.',
                        'user_id': 1
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
                    'Password mismatch',
                    value={'password_confirm': ['Passwords do not match.']}
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
