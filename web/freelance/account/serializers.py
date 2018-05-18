from rest_framework import serializers
from freelance.account.models import User
from freelance.core.utils import validate_email as email_validation


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'role',
            'password',
        )

        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
            'email': {'validators': [email_validation]},
            'password': {'write_only': True},
            'id': {'read_only': True}
        }

    def validate_email(self, value):
        email = email_validation(value)
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError('User already exists.')
        return email_validation(value)

    def validate_role(self, role):
        if role and role not in ['freelancer', 'client']:
            raise serializers.ValidationError('Invalid role')
        return role

    def validate_password(self, password):
        if len(password) < 4:
            raise serializers.ValidationError('Short password')
        return password
