from rest_framework.permissions import BasePermission
from freelance.order.models import Order


class OrderPermission(BasePermission):
    def has_permission(self, request, view):
        return request.method != 'POST' or (
            request.user and
            request.user.is_authenticated)


class ApproveFreelancerRequestPermission(BasePermission):

    def is_correct_user(self, pk, request):
        return Order.objects.filter(pk=pk, client=request.user).exists()

    def has_permission(self, request, view):
        return request.method != 'POST' or (
            request.user and request.user.is_authenticated and
            self.is_correct_user(view.kwargs.get('pk'), request))


class UpdatePermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.method not in ['PATCH', 'PUT'] or (
            request.user and request.user.is_authenticated and 
            obj.client == request.user)
