"""
Serializers for point-related models.
"""

import re

from django.core.validators import RegexValidator
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
            'blank': 'Dia da semana de abertura não pode estar vazio (YYYY-MM-DD).',
            'invalid': 'Formato de data inválido para dia de abertura (YYYY-MM-DD).'
        }

        self.fields['week_end'].error_messages = {
            'required': 'Dia da semana de fechamento é obrigatório.',
            'blank': 'Dia da semana de fechamento não pode estar vazio (YYYY-MM-DD).',
            'invalid': 'Formato de data inválido para dia de fechamento (YYYY-MM-DD).'
        }

        self.fields['open_time'].error_messages = {
            'required': 'Horário de abertura é obrigatório.',
            'blank': 'Horário de abertura não pode estar vazio hh:mm[:ss[.uuuuuu]].',
            'invalid': 'Formato de horário inválido para abertura (hh:mm[:ss[.uuuuuu]]).'
        }

        self.fields['close_time'].error_messages = {
            'required': 'Horário de fechamento é obrigatório.',
            'blank': 'Horário de fechamento não pode estar vazio hh:mm[:ss[.uuuuuu]].',
            'invalid': 'Formato de horário inválido para fechamento (hh:mm[:ss[.uuuuuu]]).'
        }

        self.fields['point_type'].error_messages = {
            'required': 'Tipo de ponto é obrigatório.',
            'blank': 'Tipo de ponto não pode estar vazio (adicionar tipos aqui?).',
            'invalid_choice': 'Tipo de ponto inválido. Escolha uma das opções disponíveis.'
        }

        self.fields['zip_code'].error_messages = {
            'required': 'CEP é obrigatório.',
            'blank': 'CEP não pode estar vazio.',
        }

        self.fields['city'].error_messages = {
            'required': 'Cidade é obrigatório.',
            'blank': 'Cidade não pode estar vazio.',
        }

        self.fields['neighborhood'].error_messages = {
            'required': 'Bairro é obrigatório.',
            'blank': 'Bairro não pode estar vazio.',
        }

        self.fields['state'].error_messages = {
            'required': 'Estado é obrigatório.',
            'blank': 'Estado não pode estar vazio.',
        }

        self.fields['street'].error_messages = {
            'required': 'Rua é obrigatória.',
            'blank': 'Rua não pode estar vazia.',
        }

        self.fields['number'].error_messages = {
            'required': 'Número é obrigatório.',
            'blank': 'Número não pode estar vazio.',
        }


class PointInfoSerializer(serializers.ModelSerializer):
    """
    Serializer for getting point information.
    """
    class Meta:
        """
        Meta class for PointInfoSerializer.
        """
        model = Point
        fields = ['name', 'description', 'week_start',
                  'week_end', 'open_time', 'close_time', 'point_type',
                  'link', 'latitude', 'longitude', 'zip_code', 'city',
                  'neighborhood', 'state', 'street', 'number']
        read_only_fields = ['name', 'description', 'week_start',
                            'week_end', 'open_time', 'close_time', 'point_type',
                            'link', 'latitude', 'longitude', 'zip_code', 'city',
                            'neighborhood', 'state', 'street', 'number']
