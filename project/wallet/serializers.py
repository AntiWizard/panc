from rest_framework import serializers

from wallet.constants import CurrencyType


class BaseSerializer(serializers.BaseSerializer):
    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class SwapSerializer(BaseSerializer):
    from_type = serializers.ChoiceField(required=True, choices=CurrencyType.CHOICES)
    to_type = serializers.ChoiceField(required=True, choices=CurrencyType.CHOICES)
    amount = serializers.DecimalField(required=True, max_digits=10, decimal_places=3)


class ConvertToUSDSerializer(BaseSerializer):
    type = serializers.ChoiceField(required=True, choices=CurrencyType.CHOICES)
    amount = serializers.DecimalField(required=True, max_digits=10, decimal_places=3)


class CashoutRequestSerializer(BaseSerializer):
    type = serializers.ChoiceField(required=True, choices=CurrencyType.CHOICES)
    amount = serializers.DecimalField(required=True, max_digits=10, decimal_places=3)
