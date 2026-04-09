from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    # Password field (write only)
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        # Fields required for user registration
        model = User
        fields = ['email', 'full_name', 'password', 'role']

    # Restrict registration to customer role only
    def validate_role(self, value):
        if value in ['superadmin', 'doctor']:
            raise serializers.ValidationError("You can only register as a customer.")
        return value

    # Create user using custom manager
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    # Input fields for login
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    # Validate user credentials
    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid credentials.")
        if not user.is_active:
            raise serializers.ValidationError("Account is disabled.")
        
        # Attach user to validated data
        data['user'] = user
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        # Serialize basic user details
        model = User
        fields = ['id', 'email', 'full_name', 'role', 'created_at']