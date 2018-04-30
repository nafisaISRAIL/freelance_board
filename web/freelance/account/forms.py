from django import forms
from django.contrib.auth import authenticate
from rest_framework import exceptions
from rest_framework.authtoken.models import Token


class LoginForm(forms.Form):
    email = forms.CharField(min_length=3, max_length=32)
    password = forms.CharField(min_length=6, max_length=128)

    def authenticate_user(self, email, password):
        user = authenticate(email=email, password=password)
        if not user:
            raise exceptions.AuthenticationFailed('Email or password are incorrect')
        token, created = Token.objects.get_or_create(user=user)
        return user, token.key

    def save(self, *args, **kwargs):
        if not self.is_valid():
            raise exceptions.ValidationError(self.errors)
        return self.authenticate_user(
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'])
