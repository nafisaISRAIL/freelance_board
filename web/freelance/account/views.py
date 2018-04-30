from rest_framework import viewsets
from rest_framework.views import APIView
from freelance.account.serializers import UserSerializer
from freelance.account.models import User
from freelance.account.forms import LoginForm
from rest_framework.response import Response
from rest_framework import permissions, exceptions
from rest_framework.authtoken.models import Token
from django.contrib.auth import logout


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class LoginView(APIView):
    def post(self, request):
        user, token = LoginForm(request.data).save()
        result = UserSerializer(user).data
        result['token'] = token
        return Response(result)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated,]

    def post(self, request):
        try:
            token = Token.objects.get(user=request.user)
            logout(request)
        except Token.DoesNotExist:
            raise exceptions.NotFound('User is not signed in')
        token.delete()
        return Response({'status': 'success'})
