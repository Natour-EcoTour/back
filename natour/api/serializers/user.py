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
        fields = ['id', 'username', 'email', 'role', 'is_active', 'is_staff']
        read_only_fields = fields


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
        fields = ['id', 'username', 'email', 'photo']
        read_only_fields = fields

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
        fields = ['id', 'username', 'email', 'is_active', 'is_staff']
        read_only_fields = fields


class UserStatusSerializer(serializers.ModelSerializer):
    """
    Serializer for changing user status.
    """
    class Meta:
        """
        Meta class for UserStatusSerializer.
        """
        model = CustomUser
        fields = ['id', 'is_active', 'deactivation_reason']

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


class UserPasswordSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user password.
    """
    class Meta:
        """
        Meta class for UserPasswordSerializer.
        """
        model = CustomUser
        fields = ['old_password', 'new_password', 'confirm_password']

        extra_kwargs = {'old_password': {'write_only': True}, 'new_password': {
            'write_only': True}, 'confirm_password': {'write_only': True}}

    old_password = serializers.CharField(
        write_only=True, required=True, error_messages={
            'required': 'Senha antiga é obrigatória.',
            'blank': 'Senha antiga não pode estar em branco.'
        })
    new_password = serializers.CharField(
        write_only=True, required=True, error_messages={
            'required': 'Nova senha é obrigatória.',
            'blank': 'Nova senha não pode estar em branco.'
        })
    confirm_password = serializers.CharField(
        write_only=True, required=True, error_messages={
            'required': 'Confirmação de senha é obrigatória.',
            'blank': 'Confirmação de senha não pode estar em branco.'
        })

    def validate_new_password(self, value):
        """
        Method to validate the new password.
        """
        if len(value) < 8 or not re.search(r'[A-Za-z]', value) or not re.search(r'[0-9]', value):
            raise serializers.ValidationError(
                'Nova senha deve ter pelo menos 8 caracteres, incluindo letras e números.')
        return value

    def validate(self, attrs):
        old_password = attrs.get('old_password')
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')

        if new_password != confirm_password:
            raise serializers.ValidationError(
                {'confirm_password': 'Nova senha e confirmação de senha não coincidem.'})

        if old_password == new_password:
            raise serializers.ValidationError(
                {'new_password': 'Nova senha não pode ser igual à senha antiga.'})

        return attrs


class NewUserPasswordSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user password without old password.
    """
    class Meta:
        """
        Meta class for NewUserPasswordSerializer.
        """
        model = CustomUser
        fields = ['password']

        extra_kwargs = {'password': {'write_only': True}}

    def validate_password(self, value):
        """
        Method to validate the new password.
        """
        if len(value) < 8 or not re.search(r'[A-Za-z]', value) or not re.search(r'[0-9]', value):
            raise serializers.ValidationError(
                'Nova senha deve ter pelo menos 8 caracteres, incluindo letras e números.')
        return value
