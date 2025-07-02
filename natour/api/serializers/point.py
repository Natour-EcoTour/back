"""
Serializers for point-related models.
"""

import re

from django.core.validators import EmailValidator, RegexValidator
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
        fields = ['name', 'description', 'week_start',
                  'week_end', 'open_time', 'close_time', 'point_type',
                  'link', 'latitude', 'longitude', 'zip_code', 'city',
                  'neighborhood', 'state', 'street', 'number']
