from django.core.serializers import serialize
from django.utils.dateparse import parse_time
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import UserSerializer

# Create your views here.
class RegisterView(APIView):
    def post(self, request):
        if User.objects.filter(username=request.data.get('username')).exists():
            return Response(
                {"message": "User with this username already exists."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(email=request.data.get('email')).exists():
            return Response(
                {"message": "User with this email already exists."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

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


class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = User.objects.filter(username=username).first()

        if user is None:
            raise AuthenticationFailed('No such user.')

        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password.')

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

class UserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        print(user)

        serializer = UserSerializer(user)

        return Response(serializer.data, status=status.HTTP_200_OK)



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
