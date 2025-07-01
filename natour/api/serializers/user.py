"""
Serializers for user-related models.
"""

import re

from django.core.validators import EmailValidator, RegexValidator
from rest_framework import serializers

from natour.api.models import CustomUser


class GenericUserSerializer(serializers.ModelSerializer):
    """
    Generic serializer for CustomUser model.
    """
    class Meta:
        """
        Meta class for GenericUserSerializer.
        """
        model = CustomUser
        fields = ['username', 'email', 'role', 'is_active', 'is_staff']


class CustomUserInfoSerializer(serializers.ModelSerializer):
    """
    Serializer for CustomUser model with additional fields.
    """

    photo = serializers.SerializerMethodField()

    class Meta:
        """
        Meta class for CustomUserInfoSerializer.
        """
        model = CustomUser
        fields = ['username', 'email', 'photo']

    def get_photo(self, obj):
        """
        Get the URL of the user's photo if it exists.
        """
        if hasattr(obj, 'photos') and obj.photos:
            return obj.photos.image.url
        return None


class CustomUserSerializer(serializers.ModelSerializer):
    """
    Serializer for CustomUser model.
    """
    class Meta:
        """
        Meta class for CustomUserSerializer.
        """
        model = CustomUser
        fields = '__all__'

        def create(self, validated_data):
            """
            Create a new CustomUser instance.
            """
            password = validated_data.pop('password')
            user = CustomUser(**validated_data)
            user.set_password(password)
            user.save()
            return user


class CreateUserSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new user.
    """
    class Meta:
        """
        Meta class for CreateUserSerializer.
        """
        model = CustomUser
        fields = ['username', 'email', 'password', 'role']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'] = serializers.CharField(
            validators=[RegexValidator(
                regex=r'^[\w.@+-]+$',
                message='Nome de usuário pode conter apenas letras, números e @/./+/-/_.'
            )],
            error_messages={
                'required': 'Nome de usuário é obrigatório.',
                'blank': 'Nome de usuário não pode estar em branco.',
            }
        )

        self.fields['email'] = serializers.CharField(
            validators=[EmailValidator(message='Email inválido.')],
            error_messages={
                'required': 'Email é obrigatório.',
                'blank': 'Email não pode estar em branco.'
            }
        )

        self.fields['password'].error_messages.update({
            'required': 'Senha é obrigatória.',
            'blank': 'Senha não pode estar em branco.',
        })

    def validate_password(self, value):
        """
        Validate the password to ensure it meets security requirements.
        """
        if len(value) < 8 or not re.search(r'[A-Za-z]', value) or not re.search(r'[0-9]', value):
            raise serializers.ValidationError(
                'Senha deve ter pelo menos 8 caracteres, incluindo letras e números.')
        return value

    def create(self, validated_data):
        email = validated_data.get('email')
        email = email.lower()
        validated_data['email'] = email

        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UpdateUserSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user information.
    """
    class Meta:
        """
        Meta class for UpdateUserSerializer.
        """
        model = CustomUser
        fields = ['username']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].error_messages.update({
            'required': 'Nome de usuário é obrigatório.',
            'blank': 'Nome de usuário não pode estar em branco.',
        })


class AllUsersSerializer(serializers.ModelSerializer):
    """
    Serializer for retriving all users.
    """
    class Meta:
        """
        Meta class for AllUsersSerializer.
        """
        model = CustomUser
        fields = ['username', 'email', 'is_active', 'is_staff']

    # def get_photo(self, obj):
    #     """
    #     Get the URL of the user's photo if it exists.
    #     """
    #     photo_obj = getattr(obj, "photos", None)
    #     if photo_obj and getattr(photo_obj, "image", None):
    #         return photo_obj.image.url
    #     return None


class UserStatusSerializer(serializers.ModelSerializer):
    """
    Serializer for changing user status.
    """
    class Meta:
        """
        Meta class for UserStatusSerializer.
        """
        model = CustomUser
        fields = ['is_active', 'deactivation_reason']

    def validate(self, attrs):
        """
        Validate the user status update.
        """
        # If is_active is being set to False, require deactivation_reason
        # First, determine the value of is_active (either from attrs or instance)
        is_active = attrs.get('is_active', getattr(
            self.instance, 'is_active', True))
        deactivation_reason = attrs.get('deactivation_reason', getattr(
            self.instance, 'deactivation_reason', ''))

        if is_active is False and not deactivation_reason:
            raise serializers.ValidationError({
                'deactivation_reason': 'Informe o motivo da desativação do usuário.'
            })

        # If user is being re-activated, clear deactivation_reason
        if is_active is True:
            # Or '' if you prefer empty string
            attrs['deactivation_reason'] = None

        return attrs
