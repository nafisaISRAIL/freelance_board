from rest_framework import routers
from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from freelance.account.views import UserViewSet, LoginView, LogoutView

router = routers.SimpleRouter(trailing_slash=False)
router.register(r'users', UserViewSet)


urlpatterns = [
    path('api/v1/', include(router.urls)),
    path('api/v1/login', LoginView.as_view()),
    path('api/v1/logout', LogoutView.as_view()),
]
