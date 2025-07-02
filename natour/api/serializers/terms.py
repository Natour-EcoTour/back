"""
Serializers for terms and conditions.
"""


from rest_framework import serializers

from natour.api.models import Terms


class CreateTermsSerializer(serializers.ModelSerializer):
    """
    Serializer for creating terms and conditions.
    """
    class Meta:
        """
        Meta class for CreateTermsSerializer.
        """
        model = Terms
        fields = ['content']


class GetTermsSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving terms and conditions.
    """
    class Meta:
        """
        Meta class for GetTermsSerializer.
        """
        model = Terms
        fields = ['content', 'updated_at']
        read_only_fields = fields


class UpadateTermsSerializer(serializers.ModelSerializer):
    """
    Serializer for updating terms and conditions.
    """
    class Meta:
        """
        Meta class for UpdateTermsSerializer.
        """
        model = Terms
        fields = ['content', 'updated_at']
