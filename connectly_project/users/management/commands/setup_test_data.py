from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from users.models import User

class Command(BaseCommand):
    help = 'Sets up test data for security testing'

    def handle(self, *args, **kwargs):
        # Create groups
        admin_group, _ = Group.objects.get_or_create(name='Admin')
        regular_group, _ = Group.objects.get_or_create(name='Regular')

        # Create test users
        admin_user = User.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='Admin123!'
        )
        admin_user.groups.add(admin_group)

        regular_user = User.objects.create_user(
            username='user_test',
            email='user@test.com',
            password='User123!'
        )
        regular_user.groups.add(regular_group)

        self.stdout.write(self.style.SUCCESS('Successfully created test data')) 