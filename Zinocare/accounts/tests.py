from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import MkulimaProfile, VetProfile

User = get_user_model()


class UserModelTest(TestCase):
    """Test the custom User model"""

    def test_create_mkulima_user(self):
        user = User.objects.create_user(
            email="farmer@test.com",
            password="testpass123",
            role="mkulima"
        )
        self.assertEqual(user.email, "farmer@test.com")
        self.assertEqual(user.role, "mkulima")
        self.assertTrue(user.check_password("testpass123"))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_vet_user(self):
        user = User.objects.create_user(
            email="vet@test.com",
            password="testpass123",
            role="vet"
        )
        self.assertEqual(user.role, "vet")

    def test_create_superuser(self):
        admin = User.objects.create_superuser(
            email="admin@test.com",
            password="adminpass123",
            username="admin",
            role="admin"
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertEqual(admin.role, "admin")

    def test_superuser_must_have_admin_role(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="bad@test.com",
                password="pass123",
                username="bad",
                role="mkulima"
            )

    def test_user_str(self):
        user = User.objects.create_user(
            email="str@test.com",
            password="pass123",
            role="mkulima"
        )
        self.assertIn("str@test.com", str(user))


class ProfileAutoCreationTest(TestCase):
    """Test that profiles are NOT auto-created by model (handled by serializer)"""

    def test_mkulima_profile_can_be_created(self):
        user = User.objects.create_user(
            email="farmer2@test.com",
            password="pass123",
            role="mkulima"
        )
        profile = MkulimaProfile.objects.create(user=user)
        self.assertEqual(profile.user, user)

    def test_vet_profile_can_be_created(self):
        user = User.objects.create_user(
            email="vet2@test.com",
            password="pass123",
            role="vet"
        )
        profile = VetProfile.objects.create(
            user=user,
            license_number="VET-001"
        )
        self.assertEqual(profile.user, user)
        self.assertEqual(profile.license_number, "VET-001")


class RegisterAPITest(TestCase):
    """Test user registration endpoint"""

    def setUp(self):
        self.client = APIClient()
        self.url = "/api/v1/accounts/register/"

    def test_register_mkulima_creates_user_and_profile(self):
        data = {
            "email": "newfarmer@test.com",
            "username": "newfarmer",
            "password": "testpass123",
            "full_name": "New Farmer",
            "role": "mkulima"
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(email="newfarmer@test.com")
        self.assertEqual(user.role, "mkulima")
        self.assertTrue(MkulimaProfile.objects.filter(user=user).exists())

    def test_register_vet_creates_user_and_profile(self):
        data = {
            "email": "newvet@test.com",
            "username": "newvet",
            "password": "testpass123",
            "full_name": "New Vet",
            "role": "vet"
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(email="newvet@test.com")
        self.assertTrue(VetProfile.objects.filter(user=user).exists())

    def test_register_duplicate_email_fails(self):
        User.objects.create_user(
            email="existing@test.com",
            password="pass123",
            role="mkulima"
        )
        data = {
            "email": "existing@test.com",
            "username": "someone",
            "password": "testpass123",
            "role": "mkulima"
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_email_fails(self):
        data = {"password": "testpass123", "role": "mkulima"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginAPITest(TestCase):
    """Test login endpoint"""

    def setUp(self):
        self.client = APIClient()
        self.url = "/api/v1/accounts/login/"
        self.user = User.objects.create_user(
            email="login@test.com",
            password="testpass123",
            username="loginuser",
            role="mkulima"
        )

    def test_login_returns_tokens(self):
        response = self.client.post(self.url, {
            "email": "login@test.com",
            "password": "testpass123"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertIn("role", response.data)
        self.assertEqual(response.data["role"], "mkulima")

    def test_login_wrong_password_fails(self):
        response = self.client.post(self.url, {
            "email": "login@test.com",
            "password": "wrongpassword"
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_nonexistent_user_fails(self):
        response = self.client.post(self.url, {
            "email": "nobody@test.com",
            "password": "testpass123"
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProfileAPITest(TestCase):
    """Test profile endpoint"""

    def setUp(self):
        self.client = APIClient()
        self.mkulima = User.objects.create_user(
            email="mkulima@test.com",
            password="pass123",
            username="mkulima",
            role="mkulima"
        )
        MkulimaProfile.objects.create(user=self.mkulima)

    def test_profile_requires_auth(self):
        response = self.client.get("/api/v1/accounts/profile/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_mkulima_profile_returns_correct_data(self):
        self.client.force_authenticate(user=self.mkulima)
        response = self.client.get("/api/v1/accounts/profile/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("farm_name", response.data)
        self.assertIn("location", response.data)
        self.assertEqual(response.data["user"]["email"], "mkulima@test.com")

    def test_profile_update(self):
        self.client.force_authenticate(user=self.mkulima)
        response = self.client.patch("/api/v1/accounts/profile/", {
            "farm_name": "Test Farm",
            "location": "Eldoret"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UserListAPITest(TestCase):
    """Test admin user list endpoint"""

    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            email="admin@test.com",
            password="adminpass",
            username="admin",
            role="admin"
        )
        self.mkulima = User.objects.create_user(
            email="farmer@test.com",
            password="pass123",
            username="farmer",
            role="mkulima"
        )

    def test_admin_can_list_users(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/api/v1/accounts/users/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_mkulima_cannot_list_users(self):
        self.client.force_authenticate(user=self.mkulima)
        response = self.client.get("/api/v1/accounts/users/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_list_users(self):
        response = self.client.get("/api/v1/accounts/users/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_filter_by_role(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/api/v1/accounts/users/?role=mkulima")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for user in response.data:
            self.assertEqual(user["role"], "mkulima")