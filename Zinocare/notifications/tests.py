from datetime import timedelta
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth import get_user_model
from accounts.models import MkulimaProfile
from livestock.models import Animal
from vaccinations.models import Vaccine, VaccinationSchedule
from notifications.models import Notification

User = get_user_model()


class NotificationModelTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="notif_farmer",
            email="notif_farmer@example.com",
            password="password123",
        )
        self.mkulima = MkulimaProfile.objects.create(user=self.user)
        self.farmer = self.user

    # Line 23: Include the required mkulima instance to satisfy the NOT NULL constraint
        self.cow = Animal.objects.create(
            mkulima=self.mkulima,
            tag_id="COW-002",
            species="cattle",
        )
        self.vaccine = Vaccine.objects.create(name="Rabies Vaccine")

        self.schedule = VaccinationSchedule.objects.create(
            animal=self.cow,
            vaccine=self.vaccine,
            next_due=timezone.now().date() + timedelta(days=7),
            interval_days=365,
        )

        
    def test_create_notification_success(self):
        """Notification in the future should save cleanly."""
        future_time = timezone.now() + timedelta(hours=2)
        notification = Notification.objects.create(
            schedule=self.schedule,
            recipient=self.farmer,
            channel=Notification.Channel.SMS,
            send_at=future_time,
            payload={"message": "Vaccine due in 7 days"},
        )
        self.assertEqual(notification.status, Notification.Status.PENDING)
        self.assertIn(f"SMS to {self.user.email}", str(notification))

    def test_past_send_at_raises_validation_error(self):
        """Validation error is raised if send_at is set to the past or now."""
        past_time = timezone.now() - timedelta(minutes=10)
        with self.assertRaises(ValidationError) as ctx:
            Notification.objects.create(
                schedule=self.schedule,
                recipient=self.farmer,
                channel=Notification.Channel.SMS,
                send_at=past_time,
            )
        self.assertIn("send_at", ctx.exception.message_dict)

    def test_unique_constraint_schedule_recipient_channel_sendat(self):
        """Duplicate notifications matching unique_notification_sched_recipient_channel_sendat should fail."""
        send_time = timezone.now() + timedelta(days=1)

        Notification.objects.create(
            schedule=self.schedule,
            recipient=self.farmer,
            channel=Notification.Channel.EMAIL,
            send_at=send_time,
        )

        with self.assertRaises(ValidationError):
            Notification.objects.create(
                schedule=self.schedule,
                recipient=self.farmer,
                channel=Notification.Channel.EMAIL,
                send_at=send_time,
            )