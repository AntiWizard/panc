from rest_framework import serializers


class BaseSerializer(serializers.BaseSerializer):
    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class SwapSerializer(BaseSerializer):
    from_type = serializers.CharField(required=True)
    to_type = serializers.CharField(required=True)
    from_amount = serializers.CharField(required=True)
    to_amount = serializers.CharField(required=True)
