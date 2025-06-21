"""
Photo Serializer
"""
from rest_framework import serializers
from natour.api.models import Photo


class PhotoSerializer(serializers.ModelSerializer):
    """
    Serializer for the Photo model.
    """
    image_url = serializers.SerializerMethodField()

    class Meta:
        """
        Meta options for the PhotoSerializer.
        """
        model = Photo
        fields = [
            'image',
            'image_url',
            'user',
            'point'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_image_url(self, obj):
        """
        Returns the URL of the image if it exists.
        """
        if obj.image:
            return obj.image.url
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
