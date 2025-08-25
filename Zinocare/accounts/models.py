import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, role="mkulima", **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, role="admin", **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if role != "admin":
            raise ValueError("Superuser must have role='admin'.")
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, role=role, **extra_fields)
class User(AbstractUser, PermissionsMixin):
    ROLE_CHOICES = [
        ("mkulima", "Mkulima"),
        ("vet", "Vet"),
        ("admin", "Admin"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, max_length=255)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="mkulima")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Needed for Django Admin access
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()
 
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["role", "username"]  

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"

class MkulimaProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="mkulima_profile")
    farm_name = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        try:
            user = self.user.full_name or self.user.email
        except AttributeError:
            user = "Unknown User"
        return f"{self.farm_name or 'Unnamed Farm'} - {user}"

class VetProfile(models.Model):
    SPECIALIZATION_CHOICES = [
        ("cattle", "Cattle"),
        ("poultry", "Poultry"),
        ("goat", "Goat"),
        ("sheep", "Sheep"),
        ("mixed", "Mixed Practice"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="vet_profile")
    license_number = models.CharField(max_length=100, unique=True)
    specialization = models.CharField(max_length=50, choices=SPECIALIZATION_CHOICES, default="mixed")  
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        try:
            user = self.user.full_name or self.user.email
        except AttributeError:
            user = "Unknown User"
        return f"{self.license_number} - {user} ({self.get_specialization_display()})"

