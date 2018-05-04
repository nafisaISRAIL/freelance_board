from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from freelance.order.models import Order
from freelance.order.serializers import (
    OrderSerializer,
    FreelancerRequestSerializer
)
from freelance.order.permissions import OrderPermission


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [OrderPermission]

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

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['client'] = request.user.pk
        serializer = OrderSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = serializer.data
        return Response(data, status=201, headers=headers)
