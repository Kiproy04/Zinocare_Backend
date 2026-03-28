from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates an admin user'

    def add_arguments(self, parser):
        parser.add_argument('--email', required=True)
        parser.add_argument('--username', required=True)
        parser.add_argument('--password', required=True)

    def handle(self, *args, **options):
        email = options['email']
        if User.objects.filter(email=email).exists():
            self.stdout.write(f'User {email} already exists')
            return
        User.objects.create_superuser(
            email=email,
            username=options['username'],
            password=options['password'],
            role='admin'
        )
        self.stdout.write(self.style.SUCCESS(f'Admin {email} created successfully'))