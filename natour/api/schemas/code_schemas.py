"""
Schema definitions for Code verification views.
"""
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample


# Send verification code schema
send_verification_code_schema = extend_schema(
    tags=['Verification'],
    summary='Send email verification code',
    description='Send a verification code to the user\'s email address.',
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'email': {'type': 'string', 'format': 'email', 'description': 'Email address to send code to'}
            },
            'required': ['email']
        }
    },
    responses={
        200: OpenApiResponse(
            description='Verification code sent successfully',
            examples=[
                OpenApiExample(
                    'Success',
                    value={'detail': 'Código de verificação enviado com sucesso.'}
                )
            ]
        ),
        400: OpenApiResponse(
            description='Bad request - invalid email or other validation errors',
            examples=[
                OpenApiExample(
                    'Invalid email',
                    value={'email': ['Enter a valid email address.']}
                )
            ]
        ),
        429: OpenApiResponse(
            description='Rate limit exceeded',
            examples=[
                OpenApiExample(
                    'Rate limited',
                    value={'detail': 'Request was throttled. Expected available in 60 seconds.'}
                )
            ]
        )
    }
)

# Verify code schema
verify_code_schema = extend_schema(
    tags=['Verification'],
    summary='Verify email code',
    description='Verify the email verification code sent to the user.',
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'email': {'type': 'string', 'format': 'email', 'description': 'Email address'},
                'code': {'type': 'string', 'description': 'Verification code received via email'}
            },
            'required': ['email', 'code']
        }
    },
    responses={
        200: OpenApiResponse(
            description='Code verified successfully',
            examples=[
                OpenApiExample(
                    'Success',
                    value={'detail': 'Código verificado com sucesso.'}
                )
            ]
        ),
        400: OpenApiResponse(
            description='Invalid or expired code',
            examples=[
                OpenApiExample(
                    'Invalid code',
                    value={'detail': 'Código inválido ou expirado.'}
                )
            ]
        )
    }
)

# Send password reset code schema
send_password_reset_code_schema = extend_schema(
    tags=['Verification'],
    summary='Send password reset code',
    description='Send a password reset code to the user\'s email address.',
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'email': {'type': 'string', 'format': 'email', 'description': 'Email address of the account to reset'}
            },
            'required': ['email']
        }
    },
    responses={
        200: OpenApiResponse(
            description='Password reset code sent successfully',
            examples=[
                OpenApiExample(
                    'Success',
                    value={'detail': 'Código de redefinição de senha enviado.'}
                )
            ]
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
        429: OpenApiResponse(description='Rate limit exceeded')
    }
)

# Verify password reset code schema
verify_password_reset_code_schema = extend_schema(
    tags=['Verification'],
    summary='Verify password reset code',
    description='Verify the password reset code and allow password change.',
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'email': {'type': 'string', 'format': 'email', 'description': 'Email address'},
                'code': {'type': 'string', 'description': 'Password reset code'},
                'new_password': {'type': 'string', 'description': 'New password to set'}
            },
            'required': ['email', 'code', 'new_password']
        }
    },
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
        400: OpenApiResponse(
            description='Invalid code or weak password',
            examples=[
                OpenApiExample(
                    'Invalid code',
                    value={'detail': 'Código inválido ou expirado.'}
                ),
                OpenApiExample(
                    'Weak password',
                    value={'new_password': ['This password is too common.']}
                )
            ]
        )
    }
)
