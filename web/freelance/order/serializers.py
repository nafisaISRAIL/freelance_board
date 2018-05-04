from rest_framework import serializers
from freelance.order.models import Order, FreelancerRequest
from freelance.account.models import User


class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = (
            'id',
            'client',
            'title',
            'description',
            'price',
            'status'
        )

        extra_kwargs = {
            'id': {'read_only': True}
        }

    def validate(self, validated_data):
        if not 'status' in validated_data:
            validated_data['status'] = 'new'
        if validated_data['client'].balance < validated_data['price']:
            raise serializers.ValidationError('Not anouth balance')
        return validated_data


class FreelancerRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FreelancerRequest
        fields = ('id', 'order', 'freelancer', 'is_active')
        extra_kwargs = {
            'id': {'read_only': True},
            'is_active': {'required': False}
        }
