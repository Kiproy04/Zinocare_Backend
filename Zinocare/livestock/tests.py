from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from accounts.models import MkulimaProfile
from livestock.models import Animal

User = get_user_model()


class AnimalAPITest(TestCase):
    """Test animal endpoints"""

    def setUp(self):
        self.client = APIClient()

        # Create mkulima user with profile
        self.mkulima = User.objects.create_user(
            email="farmer@test.com",
            password="pass123",
            username="farmer",
            role="mkulima"
        )
        self.profile = MkulimaProfile.objects.create(user=self.mkulima)

        # Create vet user
        self.vet = User.objects.create_user(
            email="vet@test.com",
            password="pass123",
            username="vet",
            role="vet"
        )

        # Create an animal for the mkulima
        self.animal = Animal.objects.create(
            mkulima=self.profile,
            name="Bessie",
            species="cattle",
            sex="female"
        )

    def test_mkulima_can_list_own_animals(self):
        self.client.force_authenticate(user=self.mkulima)
        response = self.client.get("/api/livestock/animal-list")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Bessie")

    def test_mkulima_can_add_animal(self):
        self.client.force_authenticate(user=self.mkulima)
        response = self.client.post("/api/livestock/animal-list", {
            "name": "Daisy",
            "species": "goat",
            "sex": "female"
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Animal.objects.filter(mkulima=self.profile).count(), 2)

    def test_vet_can_view_all_animals(self):
        self.client.force_authenticate(user=self.vet)
        response = self.client.get("/api/livestock/animal-list")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_vet_cannot_add_animal(self):
        self.client.force_authenticate(user=self.vet)
        response = self.client.post("/api/livestock/animal-list", {
            "name": "Daisy",
            "species": "goat",
            "sex": "female"
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_access_animals(self):
        response = self.client.get("/api/livestock/animal-list")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_mkulima_cannot_see_other_farmers_animals(self):
        # Create another farmer with their own animal
        other_farmer = User.objects.create_user(
            email="other@test.com",
            password="pass123",
            username="other",
            role="mkulima"
        )
        other_profile = MkulimaProfile.objects.create(user=other_farmer)
        Animal.objects.create(
            mkulima=other_profile,
            name="Other Animal",
            species="sheep",
            sex="male"
        )

        self.client.force_authenticate(user=self.mkulima)
        response = self.client.get("/api/livestock/animal-list")
        names = [a["name"] for a in response.data]
        self.assertNotIn("Other Animal", names)