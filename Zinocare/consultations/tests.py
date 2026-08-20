from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from accounts.models import MkulimaProfile
from consultations.models import Consultation

User = get_user_model()


class ConsultationAPITest(TestCase):
    """Test consultation endpoints"""

    def setUp(self):
        self.client = APIClient()

        self.mkulima = User.objects.create_user(
            email="farmer@test.com",
            password="pass123",
            username="farmer",
            role="mkulima"
        )
        MkulimaProfile.objects.create(user=self.mkulima)

        self.vet = User.objects.create_user(
            email="vet@test.com",
            password="pass123",
            username="vet",
            role="vet"
        )

    def test_mkulima_can_request_consultation(self):
        self.client.force_authenticate(user=self.mkulima)
        response = self.client.post("/api/v1/consultations/request/", {
            "notes": "My cow is sick"
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "REQUESTED")

    def test_vet_cannot_request_consultation(self):
        self.client.force_authenticate(user=self.vet)
        response = self.client.post("/api/v1/consultations/request/", {
            "notes": "Testing"
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_request_consultation(self):
        response = self.client.post("/api/v1/consultations/request/", {
            "notes": "Testing"
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_mkulima_can_list_own_consultations(self):
        # Create consultation
        Consultation.objects.create(
            farmer=self.mkulima,
            notes="Test consultation"
        )
        self.client.force_authenticate(user=self.mkulima)
        response = self.client.get("/api/v1/consultations/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_mkulima_can_cancel_own_consultation(self):
        consultation = Consultation.objects.create(
            farmer=self.mkulima,
            notes="To be cancelled"
        )
        self.client.force_authenticate(user=self.mkulima)
        response = self.client.patch(
            f"/api/v1/consultations/cancel/{consultation.id}/",
            {"reason": "Changed my mind"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        consultation.refresh_from_db()
        self.assertEqual(consultation.status, "CANCELLED")

    def test_mkulima_cannot_cancel_others_consultation(self):
        other_farmer = User.objects.create_user(
            email="other@test.com",
            password="pass123",
            username="other",
            role="mkulima"
        )
        MkulimaProfile.objects.create(user=other_farmer)
        consultation = Consultation.objects.create(
            farmer=other_farmer,
            notes="Other farmer's consultation"
        )
        self.client.force_authenticate(user=self.mkulima)
        response = self.client.patch(
            f"/api/v1/consultations/cancel/{consultation.id}/",
            {"reason": "Trying to cancel"}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)