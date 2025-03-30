from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Translation

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'first_name', 'last_name',
                 'organization', 'is_healthcare_provider')
        read_only_fields = ('id',)
        extra_kwargs = {
            'username': {'required': True},
            'password': {'required': True, 'min_length': 8},
            'first_name': {'required': False},
            'last_name': {'required': False},
            'organization': {'required': False},
            'is_healthcare_provider': {'required': False}
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        return value

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

class TranslationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Translation
        fields = '__all__'