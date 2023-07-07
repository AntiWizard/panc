from django.core.validators import MinValueValidator
from rest_framework import serializers

from wallet.serializers import BasicSerializer


class BuyTicketSerializer(BasicSerializer):
    ticket_count = serializers.IntegerField(required=True, validators=[MinValueValidator(1)])
