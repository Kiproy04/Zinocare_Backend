from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiResponse
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

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "admin"

class UserListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def get_queryset(self):
        User = get_user_model()
        role = self.request.query_params.get('role')
        if role:
            return User.objects.filter(role=role).order_by('-date_joined')
        return User.objects.all().order_by('-date_joined')
    
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class LoginTokenObtainPairView(TokenObtainPairView):
    serializer_class = LoginTokenObtainPairSerializer

@extend_schema(
    request=LogoutSerializer,
    responses={205: OpenApiResponse(description="Successfully logged out.")}
)
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

@extend_schema(
    responses={
        200: OpenApiResponse(description="Returns profile based on user role (Mkulima or Vet).")
    }
)
class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        user = self.request.user
        if user.role == "mkulima":
            return MkulimaProfile.objects.get(user=user)
        elif user.role == "vet":
            return VetProfile.objects.get(user=user)
        return user

    def get_serializer_class(self):
        user = self.request.user
        # During schema generation, user is anonymous
        if not hasattr(user, 'role'):
            return UserSerializer
        if user.role == "mkulima":
            return MkulimaProfileSerializer
        elif user.role == "vet":
            return VetProfileSerializer
        return UserSerializer