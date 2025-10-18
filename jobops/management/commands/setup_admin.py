from django.core.management.base import BaseCommand
from jobops.models import User

class Command(BaseCommand):
    help = 'Setup initial admin user if no users exist'

    def handle(self, *args, **options):
        if User.objects.exists():
            self.stdout.write(self.style.WARNING('Users already exist. Skipping setup.'))
            return

        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123',
            first_name='Admin',
            last_name='User',
            role=User.ROLE_ADMIN
        )

        self.stdout.write(self.style.SUCCESS('✅ Admin user created successfully!'))
        self.stdout.write('Username: admin')
        self.stdout.write('Password: admin123')
