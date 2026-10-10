import os
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth.password_validation import validate_password
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Create the initial administrator from environment variables, without resetting existing passwords.'

    def handle(self, *args, **options):
        group, _ = Group.objects.get_or_create(name='Level editors')
        group.permissions.set(Permission.objects.filter(content_type__app_label='game', codename__in=[
            'view_gamelevel', 'add_gamelevel', 'change_gamelevel', 'delete_gamelevel', 'view_gamesession',
        ]))
        username = os.environ.get('BOOTSTRAP_ADMIN_USERNAME')
        password = os.environ.get('BOOTSTRAP_ADMIN_PASSWORD')
        if not username:
            self.stdout.write('No initial admin configured. Use createsuperuser to create one.')
            return
        if User.objects.filter(username=username).exists():
            self.stdout.write('Existing administrator preserved.')
            return
        if not password:
            raise CommandError('BOOTSTRAP_ADMIN_PASSWORD is required for a new administrator.')
        user = User(username=username, email=os.environ.get('BOOTSTRAP_ADMIN_EMAIL', ''))
        user.full_clean(exclude=['password'])
        validate_password(password, user=user)
        User.objects.create_superuser(username=username, email=user.email, password=password)
        self.stdout.write(self.style.SUCCESS('Initial administrator created.'))
