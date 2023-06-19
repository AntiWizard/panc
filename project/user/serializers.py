from rest_framework import serializers

from user.utils import validate_eth_address


class BasicSerializer(serializers.Serializer):

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class VerifyLoginSerializer(BasicSerializer):
    address = serializers.CharField(max_length=42, required=True, validators=[validate_eth_address])


class LogoutSerializer(BasicSerializer):
    access = serializers.CharField(max_length=1500, required=True)
