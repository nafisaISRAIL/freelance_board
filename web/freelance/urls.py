from rest_framework import routers
from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from freelance.account.views import UserViewSet, LoginView, LogoutView
from freelance.order.views import OrderViewSet

router = routers.SimpleRouter(trailing_slash=False)
router.register(r'users', UserViewSet)
router.register(r'orders', OrderViewSet)


urlpatterns = [
    path('api/v1/', include(router.urls)),
    path('api/v1/login', LoginView.as_view()),
    path('api/v1/logout', LogoutView.as_view()),
    path('admin/', admin.site.urls),
]
