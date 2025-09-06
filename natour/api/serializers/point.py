"""
Serializers for point-related models.
"""

from rest_framework import serializers

from natour.api.models import Point


class CreatePointSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new point.
    """
    class Meta:
        """
        Meta class for CreatePointSerializer.
        """
        model = Point
        fields = ['id', 'name', 'description', 'week_start',
                  'week_end', 'open_time', 'close_time', 'point_type',
                  'link', 'latitude', 'longitude', 'zip_code', 'city',
                  'neighborhood', 'state', 'street', 'number']
        read_only_fields = ['id']

    def __init__(self, *args, **kwargs):
        """
        Initialize the serializer with custom validators.
        """
        super().__init__(*args, **kwargs)
        self.fields['name'].error_messages = {
            'required': 'Nome é obrigatório.',
            'blank': 'Nome não pode estar vazio.',
        }

        self.fields['description'].error_messages = {
            'required': 'Descrição é obrigatória.',
            'blank': 'Descrição não pode estar vazia.',
        }

        self.fields['week_start'].error_messages = {
            'required': 'Dia da semana de abertura é obrigatório.',
            'blank': 'Dia da semana de abertura não pode estar vazio (ex: Segunda-feira).',
            'invalid': 'Formato de data inválido para dia de abertura (ex: Segunda-feira).'
        }

        self.fields['week_end'].error_messages = {
            'required': 'Dia da semana de fechamento é obrigatório.',
            'blank': 'Dia da semana de fechamento não pode estar vazio (ex: Segunda-feira).',
            'invalid': 'Formato de data inválido para dia de fechamento (ex: Segunda-feira).'
        }

        self.fields['open_time'].error_messages = {
            'required': 'Horário de abertura é obrigatório.',
            'blank': 'Horário de abertura não pode estar vazio (ex: 08:00).',
            'invalid': 'Formato de horário inválido para abertura (ex: 08:00).'
        }

        self.fields['close_time'].error_messages = {
            'required': 'Horário de fechamento é obrigatório.',
            'blank': 'Horário de fechamento não pode estar vazio (ex: 08:00).',
            'invalid': 'Formato de horário inválido para fechamento (ex: 08:00).'
        }

        self.fields['point_type'].error_messages = {
            'required': 'Tipo de ponto é obrigatório.',
            'blank': 'Tipo de ponto não pode estar vazio (ex: trilha).',
            'invalid_choice': 'Tipo de ponto inválido. Escolha uma das opções disponíveis.'
        }


class PointInfoSerializer(serializers.ModelSerializer):
    """
    Serializer for getting point information.
    """
    photos = serializers.SerializerMethodField()

    class Meta:
        """
        Meta class for PointInfoSerializer.
        """
        model = Point
        fields = ['id', 'is_active', 'name', 'views', 'avg_rating', 'description', 'week_start',
                  'week_end', 'open_time', 'close_time', 'point_type',
                  'link', 'latitude', 'longitude', 'zip_code', 'city',
                  'neighborhood', 'state', 'street', 'number', 'photos']
        read_only_fields = fields

    def get_photos(self, obj):
        """
        Returns a list of photo URLs associated with the point.
        """
        return [photo.image.url for photo in obj.photos.all()]


class UserPointSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving points created by a specific user.
    """
    class Meta:
        """
        Meta class for UserPointSerializer.
        """
        model = Point
        fields = ['id', 'name', 'is_active', 'created_at',
                  'point_type', 'avg_rating', 'views']
        read_only_fields = fields


class PointStatusSerializer(serializers.ModelSerializer):
    """
    Serializer for updating the status of a point.
    """
    class Meta:
        """
        Meta class for PointStatusSerializer.
        """
        model = Point
        fields = ['id', 'is_active', 'deactivation_reason']
        read_only_fields = ['id']

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
                'deactivation_reason': 'Informe o motivo da desativação do ponto.'
            })

        # If user is being re-activated, clear deactivation_reason
        if is_active is True:
            # Or '' if you prefer empty string
            attrs['deactivation_reason'] = None

        return attrs


class PointOnMapSerializer(serializers.ModelSerializer):
    """
    Serializer for getting point information.
    """

    class Meta:
        """
        Meta class for PointInfoSerializer.
        """
        model = Point
        fields = ['id', 'name', 'point_type', 'latitude', 'longitude', 'zip_code', 'city',
                  'neighborhood', 'state', 'street', 'number']
        read_only_fields = fields


class PointMapSearchSerializer(serializers.ModelSerializer):
    """
    Serializer for searching a point by name.
    """

    class Meta:
        """
        Meta class for PointMapSearchSerializer.
        """
        model = Point
        fields = ['id', 'name']
        read_only_fields = fields


class PointApprovalSerializer(serializers.ModelSerializer):
    """
    Serializer for approving or rejecting a point.
    """
    class Meta:
        """
        Meta class for PointStatusSerializer.
        """
        model = Point
        fields = ['id', 'is_active', 'status']
        read_only_fields = fields


class PointStatusUser(serializers.ModelSerializer):
    """
    Serializer for a user to update the status of a point.
    """
    class Meta:
        """
        Meta class for PointStatusSerializer.
        """
        model = Point
        fields = ['id', 'is_active']
        read_only_fields = ['id']
