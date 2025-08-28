from django.shortcuts import render
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


class RegisterView(generics.CreateAPIView):
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

def get_profile_and_serializer(self, user, data=None, partial=False):
    if user.role == "mkulima":
        profile = MkulimaProfile.objects.get(user=user)
        serializer = MkulimaProfileSerializer(profile, data=data, partial=partial)
    elif user.role == "vet":
        profile = VetProfile.objects.get(user=user)
        serializer = VetProfileSerializer(profile, data=data, partial=partial)
    else:
        profile, serializer = None, UserSerializer(user, data=data, partial=partial) if data else UserSerializer(user)
    return profile, serializer
class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        _, serializer = self.get_profile_and_serializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        profile, serializer = self.get_profile_and_serializer(request.user, request.data, partial=True)
        if profile is None:
            return Response({"error": "Profile update not available for this role"}, status=400)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
