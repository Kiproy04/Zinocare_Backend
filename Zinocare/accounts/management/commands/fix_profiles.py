from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import MkulimaProfile, VetProfile

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates missing profiles for existing users'

    def handle(self, *args, **kwargs):
        mkulima_users = User.objects.filter(role='mkulima')
        vet_users = User.objects.filter(role='vet')

        for user in mkulima_users:
            profile, created = MkulimaProfile.objects.get_or_create(user=user)
            if created:
                self.stdout.write(f'Created MkulimaProfile for {user.email}')
            else:
                self.stdout.write(f'Profile already exists for {user.email}')

        for user in vet_users:
            profile, created = VetProfile.objects.get_or_create(user=user)
            if created:
                self.stdout.write(f'Created VetProfile for {user.email}')
            else:
                self.stdout.write(f'Profile already exists for {user.email}')

        self.stdout.write(self.style.SUCCESS('All profiles checked!'))