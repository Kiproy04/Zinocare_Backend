from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    RegisterSerializer,
    LoginTokenObtainPairSerializer,
    UserSerializer,
    MkulimaProfileSerializer,
    VetProfileSerializer,
    LogoutSerializer,
)
from .models import MkulimaProfile, VetProfile
User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class LoginTokenObtainPairView(TokenObtainPairView):
    serializer_class = LoginTokenObtainPairSerializer

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save()
        except Exception:
            return Response(
                {"detail": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            {"detail": "Successfully logged out."},
            status=status.HTTP_205_RESET_CONTENT
        )


class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Return the correct profile instance based on user role."""
        user = self.request.user
        if user.role == "mkulima":
            return MkulimaProfile.objects.get(user=user)
        elif user.role == "vet":
            return VetProfile.objects.get(user=user)
        return user  

    def get_serializer_class(self):
        """Return the correct serializer based on user role."""
        user = self.request.user
        if user.role == "mkulima":
            return MkulimaProfileSerializer
        elif user.role == "vet":
            return VetProfileSerializer
        return UserSerializer
