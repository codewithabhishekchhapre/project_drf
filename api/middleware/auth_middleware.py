# middleware/auth_middleware.py
from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError, AuthenticationFailed
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class JWTAuthMiddleware(MiddlewareMixin):
    EXEMPT_PATHS = [
        "/v1/api/login/",
        "/v1/api/signup/",
        "/v1/api/send-otp/",
        "/v1/api/verify-otp/",
        "/v1/api/reset-password/"
    ]

    def process_request(self, request):
        # Skip authentication for exempt paths
        if any(request.path.startswith(path) for path in self.EXEMPT_PATHS):
            return None
            
        # Handle OPTIONS preflight requests
        if request.method == 'OPTIONS':
            return None

        jwt_auth = JWTAuthentication()
        token = request.COOKIES.get("access_token")
        
        if not token:
            return Response(
                {"error": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            # Authenticate the token
            validated_token = jwt_auth.get_validated_token(token)
            
            # Manually get the user from the token
            try:
                user_id = validated_token[jwt_auth.user_id_field]
                user = User.objects.get(pk=user_id)
                
                if not user.is_active:
                    return Response(
                        {"error": "User account is disabled."},
                        status=status.HTTP_401_UNAUTHORIZED
                    )
                
                # Set the authenticated user on the request
                request.user = user
                request.auth = validated_token
                return None
                
            except User.DoesNotExist:
                return Response(
                    {"error": "User not found"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
                
        except InvalidToken as e:
            return Response(
                {"error": "Invalid token"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except TokenError as e:
            return Response(
                {"error": f"Token error: {str(e)}"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            return Response(
                {"error": f"Authentication error: {str(e)}"},
                status=status.HTTP_401_UNAUTHORIZED
            )