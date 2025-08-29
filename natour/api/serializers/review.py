"""
Serializers for point review-related models.
"""

from rest_framework import serializers

from natour.api.models import PointReview


class CreateReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new point review.
    """
    class Meta:
        """
        Meta class for CreateReviewSerializer.
        """
        model = PointReview
        fields = ['id', 'rating']
        read_only_fields = ['id']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rating'].error_messages = {
            'required': 'Avaliação é obrigatória.',
            'blank': 'Avaliação não pode estar vazia.',
            'invalid': 'Avaliação deve ser um número entre 1 e 5.'
        }


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for point review information.
    """
    username = serializers.CharField(source='user.username', read_only=True)
    point_name = serializers.CharField(source='point.name', read_only=True)

    class Meta:
        """
        Meta Class for ReviewSerializer.
        """
        model = PointReview
        fields = ['id', 'username', 'point_name', 'rating']
        read_only_fields = fields
