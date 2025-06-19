import re

from django.core.validators import EmailValidator, RegexValidator

from rest_framework import serializers

from ..models import CustomUser, Point, PointReview, Terms


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'

        def create(self, validated_data):
            password = validated_data.pop('password')
            user = CustomUser(**validated_data)
            user.set_password(password)
            user.save()
            return user


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
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
