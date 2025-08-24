"""
Photo Serializer
"""
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from natour.api.models import Photo


class PhotoSerializer(serializers.ModelSerializer):
    """
    Serializer for the Photo model.
    """
    image_url = serializers.SerializerMethodField()
    image_public_id = serializers.SerializerMethodField()

    class Meta:
        """
        Meta options for the PhotoSerializer.
        """
        model = Photo
        fields = [
            'image',
            'image_url',
            'user',
            'point',
            'image_public_id',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_image_url(self, obj):
        """
        Returns the URL of the image if it exists.
        """
        if obj.image:
            return obj.image.url
        return None

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_image_public_id(self, obj):
        """
        Returns the public ID of the image if it exists.
        """
        if obj.image:
            return obj.image.public_id
        return None

    def validate(self, attrs):
        user = attrs.get('user')
        point = attrs.get('point')
        if not user and not point:
            raise serializers.ValidationError(
                "Foto deve ser atribuida a um usuário ou a um ponto.")
        if user and point:
            raise serializers.ValidationError(
                "Foto só pode ser atribuida a um usuário ou a um ponto, não aos dois.")
        return attrs

    def create(self, validated_data):
        photo = super().create(validated_data)
        if photo.image:
            photo.public_id = photo.image.public_id
            photo.save()
        return photo

    def update(self, instance, validated_data):
        photo = super().update(instance, validated_data)
        if photo.image:
            photo.public_id = photo.image.public_id
            photo.save()
        return photo


class PhotoIDSerializer(serializers.ModelSerializer):
    """
    Serializer for Photo ID.
    """
    class Meta:
        """
        Meta options for the PhotoIDSerializer.
        """
        model = Photo
        fields = ['id', 'public_id']
        read_only_fields = ['id', 'public_id']
