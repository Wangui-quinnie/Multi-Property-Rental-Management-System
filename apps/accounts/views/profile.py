from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from apps.core.api.responses import success_response
from apps.core.api.mixins import CurrentUserMixin

from apps.accounts.serializers import (
    UserSerializer,
    ProfileUpdateSerializer,
    ChangePasswordSerializer,
)


class ProfileView(CurrentUserMixin, APIView):
    permission_classes = [IsAuthenticated]
    @extend_schema(responses=UserSerializer)
    def get(self, request):
        serializer = UserSerializer(self.user)
        return success_response(data=serializer.data, message="Profile retrieved successfully.")
    
    @extend_schema(request=ProfileUpdateSerializer, responses=UserSerializer)
    def patch(self, request):
        serializer = ProfileUpdateSerializer(self.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(
            data=UserSerializer(self.user).data,
            message="Profile updated successfully.",
        )


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    @extend_schema(request=ChangePasswordSerializer, responses=None)

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(message="Password changed successfully.")