from rest_framework import serializers

from wallet.constants import CurrencyType


class BasicSerializer(serializers.Serializer):
    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class SwapSerializer(BasicSerializer):
    from_type = serializers.ChoiceField(required=True, choices=CurrencyType.CHOICES)
    to_type = serializers.ChoiceField(required=True, choices=CurrencyType.CHOICES)
    from_amount = serializers.DecimalField(required=True, max_digits=10, decimal_places=3)

class SecondSwapSerializer(BasicSerializer):
    from_type = serializers.ChoiceField(required=True, choices=CurrencyType.CHOICES)
    to_type = serializers.ChoiceField(required=True, choices=CurrencyType.CHOICES)
    from_amount = serializers.DecimalField(required=True, max_digits=10, decimal_places=3)
    to_amount = serializers.DecimalField(required=True, max_digits=10, decimal_places=3)
    ratio_balance = serializers.DecimalField(required=True, max_digits=10, decimal_places=3)

class ConvertToUSDSerializer(BasicSerializer):
    type = serializers.ChoiceField(required=True, choices=CurrencyType.CHOICES)
    amount = serializers.DecimalField(required=True, max_digits=10, decimal_places=3)


class CashoutRequestSerializer(BasicSerializer):
    type = serializers.ChoiceField(required=True, choices=CurrencyType.CHOICES)
    amount = serializers.DecimalField(required=True, max_digits=10, decimal_places=3)
