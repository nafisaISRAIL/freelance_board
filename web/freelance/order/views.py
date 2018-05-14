from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from freelance.account.models import User
from freelance.order.models import Order
from freelance.order.serializers import (
    OrderSerializer,
    FreelancerRequestSerializer,
    ActivateOrderSerializer
)
from freelance.order.permissions import OrderPermission, ApproveFreelancerRequestPermission, UpdatePermission

from django.shortcuts import get_object_or_404


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [OrderPermission, UpdatePermission]

    @action(methods=['post'], detail=True)
    def freelancer_request(self, request, pk=None):
        data = {}
        data['freelancer'] = request.user.id
        data['order'] = pk
        serializer = FreelancerRequestSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    @action(methods=['post'], detail=True, permission_classes=[ApproveFreelancerRequestPermission,])
    def approve_freelancer_request(self, request, pk=None, user_pk=None):
        order = get_object_or_404(Order, pk=pk)
        data = {
            'freelancer': request.data.get('freelancer'),
            'order': pk,
            'client': request.user.pk
        }
        serializer = ActivateOrderSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(OrderSerializer(order).data, status=200)

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['client'] = request.user.pk
        serializer = OrderSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = serializer.data
        return Response(data, status=201, headers=headers)

    def list(self, request, *args, **kwargs):
        user_pk = kwargs.get('user_pk')
        queryset = self.get_queryset()
        if user_pk:
            queryset = queryset.filter(client_id=user_pk)
        serializer = OrderSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
