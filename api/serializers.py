from rest_framework import serializers
from .models import CustomUser
import re

class SignupSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    mobile = serializers.CharField(max_length=15)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    role = serializers.ChoiceField(choices=['admin', 'user', 'teacher'])
    gender = serializers.ChoiceField(choices=['male', 'female', 'other'])
    city = serializers.CharField(max_length=100, required=False, allow_blank=True)
    state = serializers.CharField(max_length=100, required=False, allow_blank=True)
    country = serializers.CharField(max_length=100, required=False, allow_blank=True)

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def validate_mobile(self, value):
        pattern = r'^[6-9]\d{9}$'   # Indian mobile validation
        if not re.match(pattern, value):
            raise serializers.ValidationError("Enter a valid mobile number")
        if CustomUser.objects.filter(mobile=value).exists():
            raise serializers.ValidationError("Mobile number already exists")
        return value

    def validate_role(self, value):
        valid_roles = ['admin', 'user', 'teacher']
        if value not in valid_roles:
            raise serializers.ValidationError("Invalid role. Choose from admin, user, teacher.")
        return value

    def validate_gender(self, value):
        valid_genders = ['male', 'female', 'other']
        if value not in valid_genders:
            raise serializers.ValidationError("Invalid gender. Choose from male, female, other.")
        return value

    def create(self, validated_data):
        return CustomUser.objects.create(**validated_data)
