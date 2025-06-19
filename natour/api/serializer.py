"""
Module for serializers used in the Natour API.
"""

from rest_framework import serializers

from .models import Point, PointReview, Terms


class PointSerializer(serializers.ModelSerializer):
    class Meta:
        model = Point
        fields = '__all__'


class PointReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = PointReview
        fields = '__all__'


class TermsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Terms
        fields = '__all__'
