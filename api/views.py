from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import SignupSerializer
from .serializers import LoginSerializer
from .serializers import OtpSerializer;
from .models import CustomUser, Otp
import random
from django.utils import timezone
import datetime

@api_view(['POST'])
def signup(request):
    serializer = SignupSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data["user"]
        # return user data
        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "mobile": user.mobile,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
            "gender": user.gender,
            "city": user.city,
            "state": user.state,
            "country": user.country,
            "is_email_verified": user.is_email_verified,
            "is_mobile_verified": user.is_mobile_verified,
            "is_profile_created": user.is_profile_created,
        }
        return Response({"message": "Login successful", "user": user_data}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def generate_otp():
    return str(random.randint(100000, 999999))

@api_view(['POST'])
def send_otp(request):
    serializer = OtpSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        otp_type = serializer.validated_data['otp_type']

        # generate otp
        otp = generate_otp()
        expires_at = timezone.now() + datetime.timedelta(minutes=5)

       # check if otp already exists for this email + type
        otp_obj = Otp.objects.filter(email=email, otp_type=otp_type).first()

        if otp_obj:
            # ✅ update existing OTP
            otp_obj.otp = otp
            otp_obj.expires_at = expires_at
            otp_obj.save()
            message = "OTP updated successfully"
            status_code = status.HTTP_200_OK
        else:
            # ✅ create new OTP record
            Otp.objects.create(
                email=email,
                otp_type=otp_type,
                otp=otp,
                expires_at=expires_at
            )
        return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

