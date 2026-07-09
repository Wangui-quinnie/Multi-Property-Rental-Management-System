from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from apps.core.api.responses import success_response
from apps.core.api.mixins import CurrentUserMixin
from .serializers import (
    LoginSerializer,
    UserSerializer,
    ProfileUpdateSerializer,
    ChangePasswordSerializer,
    LogoutSerializer,
)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return success_response(
            data={
                "access": serializer.validated_data["access"],
                "refresh": serializer.validated_data["refresh"],
                "user": UserSerializer(serializer.validated_data["user"]).data,
            },
            message="Login successful.",
            status_code=status.HTTP_200_OK,
        )


class ProfileView(CurrentUserMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(self.user)
        return success_response(
            data=serializer.data,
            message="Profile retrieved successfully.",
        )

    def patch(self, request):
        serializer = ProfileUpdateSerializer(
            self.user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return success_response(
            data=UserSerializer(request.user).data,
            message="Profile updated successfully.",
        )


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return success_response(message="Password changed successfully.")


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return success_response(message="Logged out successfully.")