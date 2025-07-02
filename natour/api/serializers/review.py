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
        fields = ['rating']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rating'].error_messages = {
            'required': 'Avaliação é obrigatória.',
            'blank': 'Avaliação não pode estar vazia.',
            'invalid': 'Avaliação deve ser um número entre 1 e 5.'
        }
