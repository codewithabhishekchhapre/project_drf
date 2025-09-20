from rest_framework import serializers
from .models import CustomUser
import re
from django.contrib.auth.hashers import check_password


class SignupSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    mobile = serializers.CharField(max_length=15)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    role = serializers.ChoiceField(choices=['admin', 'user', 'teacher'])
    gender = serializers.ChoiceField(choices=['male', 'female', 'other'], required=False)

    first_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=100, required=False, allow_blank=True)

    city = serializers.CharField(max_length=100, required=False, allow_blank=True)
    state = serializers.CharField(max_length=100, required=False, allow_blank=True)
    country = serializers.CharField(max_length=100, required=False, allow_blank=True)

    # These fields should not be set by user directly during signup
    is_email_verified = serializers.BooleanField(read_only=True)
    is_mobile_verified = serializers.BooleanField(read_only=True)
    is_profile_created = serializers.BooleanField(read_only=True)

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



class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField()  # username OR email OR mobile
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate(self, data):
        identifier = data.get("identifier")
        password = data.get("password")

        try:
            # Try username, then email, then mobile
            user = CustomUser.objects.filter(username=identifier).first() \
                or CustomUser.objects.filter(email=identifier).first() \
                or CustomUser.objects.filter(mobile=identifier).first()

            if not user:
                raise serializers.ValidationError("User not found.")

            # Check password
            # if not check_password(password, user.password):
            if user.password != password:
                raise serializers.ValidationError("Invalid credentials.")

            # Check verification
            if not user.is_email_verified or not user.is_mobile_verified:
                raise serializers.ValidationError("Please verify your email and mobile before login.")

            data["user"] = user
            return data

        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Invalid login credentials.")




# email , otp_type ('email_verification', 'password_reset')

class OtpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp_type = serializers.ChoiceField(choices=['email_verification', 'password_reset'])
    
    def validate(self , data):
        email= data.get('email')
        otp_type= data.get('otp_type')
        
        user = CustomUser.objects.filter(email=email).first()

        if otp_type == "email_verification" and user.is_email_verified:
            raise serializers.ValidationError("User already verified")
        
        if otp_type == "password_reset" and not user.is_email_verified:
           raise serializers.ValidationError("Inactive users cannot reset password")
        
        return data
    
    def validate_email(self, value):
        if not CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email does not exist")
        return value
    
    def validate_otp_type(self, value):
        valid_types = ['email_verification', 'password_reset']
        if value not in valid_types:
            raise serializers.ValidationError("Invalid OTP type. Choose from email_verification, password_reset.")
        return value
    

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    verify_otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True, min_length=6)

    def validate(self, data):
        email = data.get("email")
        verify_otp = data.get("verify_otp")
        new_password = data.get("new_password")
        confirm_password = data.get("confirm_password")

        # confirm passwords match
        if new_password != confirm_password:
            raise serializers.ValidationError("Passwords do not match")

        # check user exists
        from .models import CustomUser
        user = CustomUser.objects.filter(email=email).first()
        if not user:
            raise serializers.ValidationError("User not found")

        # match otp with what verify_otp API gave
        if not verify_otp:
            raise serializers.ValidationError("OTP verification required before reset password")

        data["user"] = user
        return data    
        
       

class ImageUploadSerializer(serializers.Serializer):
    image = serializers.ImageField(required=True)
    
    
class MultiImageUploadSerializer(serializers.Serializer):
    images = serializers.ListField(
        child=serializers.ImageField(),
        allow_empty=False
    )
            
        
from rest_framework import serializers
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        exclude = ["password"]  # don't expose passwords
       