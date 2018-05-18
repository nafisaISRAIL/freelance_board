from rest_framework import serializers
from freelance.order.models import Order, FreelancerRequest
from freelance.account.models import User
from freelance.payment.models import TransactionLog


class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = '__all__'

        extra_kwargs = {
            'id': {'read_only': True}
        }

    def validate_status(self, value):
        if not value:
            value = 'new'
        return value

    def create(self, validated_data):
        if validated_data['client'].balance < validated_data['price']:
            raise serializers.ValidationError('Not anouth balance')
        obj = Order.objects.create(**validated_data)
        return obj

    def update(self, instance, validated_data):
        status = validated_data.get('status')
        if status == 'finished' and instance.freelancer and instance.status != 'finished':
            TransactionLog.transfer(
                amount=instance.price,
                freelancer_email=instance.freelancer.email,
                client_email=instance.client.email,
                status='success'
            )
            instance.approved = True
        instance.status = status
        instance.save()
        return instance


class FreelancerRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FreelancerRequest
        fields = ('id', 'order', 'freelancer', 'is_active')
        extra_kwargs = {
            'id': {'read_only': True},
            'is_active': {'required': False}
        }


class ActivateOrderSerializer(serializers.Serializer):
    freelancer = serializers.IntegerField()
    order = serializers.IntegerField()

    def __init__(self, *args, **kwargs):
        super(ActivateOrderSerializer, self).__init__(*args, **kwargs)
        self.freelancer = self.get_freelancer(kwargs.get('data'))
        self.order = self.get_order(kwargs.get('data'))
        self.client = self.get_client(kwargs.get('data'))

    def get_freelancer(self, context):
        freelancer = User.objects.filter(pk=context.get('freelancer')).first()
        if not freelancer:
            raise serializers.ValidationError('No user here')
        return freelancer

    def get_order(self, context):
        order = Order.objects.filter(pk=context.get('order')).first()
        client_balance = User.objects.filter(pk=context.get('client')).values_list('freeze_balance', flat=True).first()
        if order:
            if order.freelancer:
                raise serializers.ValidationError('Order is active')
            elif client_balance < order.price:
                raise serializers.ValidationError('Not anouth balance')
        return order

    def get_client(self, context):
        client_balance = User.objects.filter(pk=context.get('client')).values_list('freeze_balance', flat=True).first()
        if client_balance < self.order.price:
            raise serializers.ValidationError('Not anouth balance')
        return client_balance

    def save(self):
        self.order.activate(self.freelancer)
        return self.order
