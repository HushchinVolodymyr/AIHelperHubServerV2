import json

from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
import requests

from .models import User
from .serializers import UserSerializer
from server.utils import captcha_v2_verify, captcha_v3_verify, ok_request, bad_request


# Create your views here.
class EchoView(APIView):
    def get(self, request): return ok_request("This is a echo GET request!")

# Register view
class RegisterView(APIView):
    def post(self, request):
        # Get data from request
        request_data = json.loads(request.body)

        # Check if user with this username already exist
        if User.objects.filter(username=request_data['userData']['username']).exists():
            return bad_request("User with this username already exists.")

        # Check if user with this email already exist
        if User.objects.filter(email=request_data["userData"]['email']).exists():
            return bad_request("User with this email already exists.")

        # Check if token provided
        if (request_data['token'] in ''):
            return bad_request("No ReCaptcha token provided")

        # Validate reCaptcha token by type
        if (request_data['captchaType'] == 'v2'):
            if captcha_v2_verify(request_data['token']) is False:
                return bad_request("ReCaptcha failed.")

        elif (request_data['captchaType'] == 'v3'):
            if captcha_v3_verify(request_data['token']) is False:
                return bad_request("ReCaptcha failed.")
        else:
            return bad_request("No reCaptcha type provided")


        serializer = UserSerializer(data=request_data["userData"])
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        user.set_password(request.data.get('password'))
        user.save()

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        response = Response({
            "user": serializer.data,
            "token": access_token,
        }, status=status.HTTP_201_CREATED)

        response.set_cookie('refresh_token', refresh_token, httponly=True, secure=True)
        response.set_cookie('access_token', access_token, httponly=True, secure=True)

        return response


# Login view
class LoginView(APIView):
    def post(self, request):
        # Get data from request
        request_data = json.loads(request.body)

        # Check if token provided
        if (request_data['token'] in ''): return bad_request("No ReCaptcha token provided")

        # Validate reCaptcha token by type
        if request_data['captchaType'] == 'v2':
            if not captcha_v2_verify(request_data['token']):
                return bad_request("ReCaptcha failed.")

        elif request_data['captchaType'] == 'v3':
            if not captcha_v3_verify(request_data['token']):
                return bad_request("ReCaptcha failed.")

        else: return bad_request("No reCaptcha type provided")

        user = User.objects.filter(username=request_data['userData']['username']).first()

        if user is None:
            raise AuthenticationFailed('No such user.')

        if not user.check_password(request_data['userData']['password']):
            raise AuthenticationFailed("Check user data!")

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        serializer_data = UserSerializer(user)

        response = Response({
            "user": serializer_data.data,
            "token": access_token,
        }, status=status.HTTP_200_OK)

        response.set_cookie(
            'refresh_token',
            refresh_token,
            httponly=True,
            secure=True,
            samesite='None'
        )
        response.set_cookie('access_token', access_token, httponly=True, secure=True)

        return response

# Google login view
class GoogleLoginView(APIView):
    def post(self, request):
        access_token = request.data.get('accessToken')

        if not access_token:
            return Response({"message": "Access token is required."}, status=status.HTTP_400_BAD_REQUEST)

        google_user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        response = requests.get(
            google_user_info_url,
            headers={"Authorization": f"Bearer {access_token}"}
        )

        if response.status_code != 200:
            return Response({"detail": "Invalid Google token."}, status=status.HTTP_400_BAD_REQUEST)

        user_info = response.json()
        email = user_info.get('email')
        username = user_info.get('name')

        user, created = User.objects.get_or_create(email=email, defaults={"username": username})

        if created:
            user.set_unusable_password()
            user.save()

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        serializer_data = UserSerializer(user)

        response = Response({
            "user": serializer_data.data,
            "token": access_token,
        }, status=status.HTTP_200_OK)

        response.set_cookie(
            'refresh_token',
            refresh_token,
            httponly=True,
            secure=True,
            samesite='None'
        )
        response.set_cookie('access_token', access_token, httponly=True, secure=True)

        return response

# User view
class UserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        serializer = UserSerializer(user)

        return Response(serializer.data, status=status.HTTP_200_OK)

# Logout view
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            refresh_token = request.COOKIES.get('refresh_token')

            if not refresh_token:
                return Response({"message": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()

            response = Response({"message": "Successfully logged out."}, status=status.HTTP_205_RESET_CONTENT)
            response.delete_cookie('access_token')
            response.delete_cookie('refresh_token')

            return response
        except Exception as e:
            print(f"Error during logout: {e}")
            return Response({"message": "Failed to logout: " + str(e)}, status=status.HTTP_400_BAD_REQUEST)


