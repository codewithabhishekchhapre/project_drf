from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
import cloudinary.uploader
from rest_framework.response import Response
from rest_framework import status
from .serializers import SignupSerializer
from .serializers import LoginSerializer ,ResetPasswordSerializer,UserSerializer
from .serializers import OtpSerializer;
from .serializers import ImageUploadSerializer, MultiImageUploadSerializer
from .models import CustomUser, Otp
import random
from django.utils import timezone
import datetime
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login as django_login


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
        
         # ✅ Create JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
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

        response = Response({
            "message": "Login successful",
            "user": user_data,
        }, status=status.HTTP_200_OK)

        # 🍪 Set tokens in cookies
        response.set_cookie(
            key="access_token",
            value=str(access_token),
            httponly=True,      # cannot be accessed by JavaScript
            secure=False,       # True in production with HTTPS
            samesite="Lax"
        )
        response.set_cookie(
            key="refresh_token",
            value=str(refresh_token),
            httponly=True,
            secure=False,
            samesite="Lax"
        )

        return response

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


@api_view(['POST'])
def verify_otp(request):
    email = request.data.get("email")
    otp_type = request.data.get("otp_type")
    otp = request.data.get("otp")

    if not email or not otp_type or not otp:
        return Response({"error": "Email, otp_type, and otp are required"}, status=status.HTTP_400_BAD_REQUEST)

    # fetch otp object
    otp_obj = Otp.objects.filter(email=email, otp_type=otp_type).first()

    if not otp_obj:
        return Response({"error": "No OTP found for this request"}, status=status.HTTP_400_BAD_REQUEST)

    # check expiry
    if otp_obj.expires_at < timezone.now():
        return Response({"error": "OTP expired"}, status=status.HTTP_400_BAD_REQUEST)

    # check value
    
    if otp_obj.otp != otp:
        return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
    verify_otp=otp_obj.otp
    # ✅ OTP is correct
    user = CustomUser.objects.filter(email=email).first()

    if otp_type == "email_verification":
        user.is_email_verified = True
        user.save()
        otp_obj.delete()  # optional: remove used OTP
        return Response({"message": "Email verified successfully"}, status=status.HTTP_200_OK)

    elif otp_type == "password_reset":
        # here we just confirm OTP, later frontend can allow password reset
        
        otp_obj.delete()
        return Response({"message": "OTP verified, you can reset your password","verify_otp":verify_otp}, status=status.HTTP_200_OK)

    return Response({"error": "Invalid OTP type"}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
def reset_password(request):
    serializer = ResetPasswordSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data["user"]
        new_password = serializer.validated_data["new_password"]

        # ✅ update password
        user.set_password(new_password)
        user.save()

        return Response({"message": "Password reset successful"}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def upload_single_image(request):
    serializer = ImageUploadSerializer(data=request.data)
    if serializer.is_valid():
        image = serializer.validated_data["image"]
        upload_result = cloudinary.uploader.upload(image)
        return Response({"url": upload_result["secure_url"]}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def upload_multiple_images(request):
    
    serializer = MultiImageUploadSerializer(data=request.data)
    if serializer.is_valid():
        urls = []
        for image in serializer.validated_data["images"]:
            upload_result = cloudinary.uploader.upload(image)
            urls.append(upload_result["secure_url"])
        return Response({"urls": urls}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@api_view(["GET"])
def get_all_users(request):
    user = request.user

    if not user or not user.is_authenticated:
        return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

    if user.role == "admin":
        queryset = CustomUser.objects.all()
    elif user.role == "teacher":
        queryset = CustomUser.objects.filter(role="user")
    else:  # role == "user"
        return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

    serializer = UserSerializer(queryset, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)