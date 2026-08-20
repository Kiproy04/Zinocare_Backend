import datetime
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from accounts.models import MkulimaProfile
from livestock.models import Animal
from vaccinations.models import (
    Vaccine,
    VaccineTargetSpecies,
    VaccinationSchedule,
    VaccinationRecord,
)

User = get_user_model()


class VaccinationModelsTestCase(TestCase):

    def setUp(self):
        # Create user and profiles
        self.user = User.objects.create_user(
            username="farmer",
            email="farmer@example.com",
            password="password123",
        )
        # If a signal automatically creates the profile, use self.user.mkulimaprofile (or related name)
        self.mkulima = MkulimaProfile.objects.create(user=self.user)

        self.vet = User.objects.create_user(
            username="vet_jane",
            email="jane@example.com",
            password="password123",
            role="vet",
            first_name="Jane",
            last_name="Doe",
        )
    

        # Create target species
        self.species_cattle = VaccineTargetSpecies.objects.create(
            species=VaccineTargetSpecies.Species.CATTLE
        )
        self.species_goat = VaccineTargetSpecies.objects.create(
            species=VaccineTargetSpecies.Species.GOAT
        )

        # Create animal (Assuming Animal model has 'species' and 'tag_id' fields)
        self.cow = Animal.objects.create(
            mkulima=self.mkulima,
            tag_id="COW-001",
            species="cattle",
        )
        self.goat = Animal.objects.create(
            mkulima=self.mkulima,
            tag_id="GOAT-001",
            species="goat",
        )

        # Create vaccine and set target species
        self.anthrax_vaccine = Vaccine.objects.create(
            name="Anthrax Spore Vaccine",
            dose="2ml fixed dose",
            route=Vaccine.Route.SUBCUTANEOUS,
            recommended_interval_days=365,
        )
        self.anthrax_vaccine.target_species.add(self.species_cattle)

    # --- Vaccine Tests ---
    def test_vaccine_creation_and_str(self):
        self.assertEqual(str(self.anthrax_vaccine), "Anthrax Spore Vaccine")
        self.assertEqual(self.anthrax_vaccine.target_species.count(), 1)

    # --- VaccinationSchedule Tests ---
    def test_schedule_valid_species(self):
        """Schedule creation succeeds when animal species is in vaccine target species."""
        schedule = VaccinationSchedule.objects.create(
            animal=self.cow,
            vaccine=self.anthrax_vaccine,
            next_due=datetime.date.today() + datetime.timedelta(days=30),
            interval_days=365,
        )
        self.assertEqual(
            str(schedule), f"Schedule: {self.cow.tag_id} - {self.anthrax_vaccine.name}"
        )

    def test_schedule_invalid_species_raises_validation_error(self):
        """Schedule fails clean() validation if animal species is not allowed."""
        with self.assertRaises(ValidationError) as ctx:
            VaccinationSchedule.objects.create(
                animal=self.goat,  # Goat is not in anthrax_vaccine target species
                vaccine=self.anthrax_vaccine,
                next_due=datetime.date.today() + datetime.timedelta(days=30),
                interval_days=365,
            )
        self.assertIn("animal", ctx.exception.message_dict)

    def test_schedule_unrestricted_vaccine(self):
        """Vaccine without target_species restriction accepts any animal species."""
        generic_vaccine = Vaccine.objects.create(name="Multivitamin Boost")
        schedule = VaccinationSchedule.objects.create(
            animal=self.goat,
            vaccine=generic_vaccine,
            next_due=datetime.date.today() + datetime.timedelta(days=10),
            interval_days=30,
        )
        self.assertIsNotNone(schedule.pk)

    # --- VaccinationRecord Tests ---
    def test_record_valid_creation_and_str(self):
        """Record succeeds when animal species matches and checks __str__ with user full name."""
        record = VaccinationRecord.objects.create(
            animal=self.cow,
            vaccine=self.anthrax_vaccine,
            performed_by=self.vet,
            date_administered=datetime.date.today(),
            batch_number="BATCH-2026-X",
        )
        self.assertIn("Jane Doe", str(record))

    def test_record_str_fallback_without_performed_by(self):
        """Test __str__ output when performed_by is None."""
        record = VaccinationRecord.objects.create(
            animal=self.cow,
            vaccine=self.anthrax_vaccine,
            performed_by=None,
            date_administered=datetime.date.today(),
        )
        self.assertIn("Unknown", str(record))

    def test_record_invalid_species_raises_validation_error(self):
        """Record fails clean() validation when species does not match vaccine target."""
        with self.assertRaises(ValidationError) as ctx:
            VaccinationRecord.objects.create(
                animal=self.goat,
                vaccine=self.anthrax_vaccine,
                performed_by=self.vet,
                date_administered=datetime.date.today(),
            )
        self.assertIn("animal", ctx.exception.message_dict)