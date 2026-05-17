"""
Serializers for users
"""

from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'name', 'phone_number', 'is_tenant',
                  'is_landlord', 'role', 'date_joined')
        read_only_fields = ('id', 'email', 'date_joined', 'role')


# Selializer for creating a new user
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)
    role_choice = serializers.ChoiceField(
        choices=['tenant', 'landlord', 'both'],
        write_only=True,
        required=True
    )

    class Meta:
        model = User
        fields = ('email', 'name', 'password', 'password2', 'role_choice')

    # Passwords must match
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password2": "The passwords do not match"})
        return attrs

    # Creating a user with the correct roles
    def create(self, validated_data):
        role_choice = validated_data.pop('role_choice')
        validated_data.pop('password2')

        # Setting up roles
        if role_choice == 'tenant':
            validated_data['is_tenant'] = True
            validated_data['is_landlord'] = False
        elif role_choice == 'landlord':
            validated_data['is_tenant'] = False
            validated_data['is_landlord'] = True
        else:
            validated_data['is_tenant'] = True
            validated_data['is_landlord'] = True

        user = User.objects.create_user(**validated_data)
        return user
