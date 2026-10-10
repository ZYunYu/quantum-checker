from getpass import getpass
from django.contrib.auth.models import User, Group
from django.contrib.auth.password_validation import validate_password
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError


class Command(BaseCommand):
    help = 'Create a staff account that can edit levels, without granting access to user permissions.'

    def add_arguments(self, parser):
        parser.add_argument('username')

    def handle(self, *args, **options):
        username = options['username']
        if User.objects.filter(username=username).exists():
            raise CommandError('Username already exists.')
        password = getpass('Editor password: ')
        if password != getpass('Confirm password: '):
            raise CommandError('Passwords do not match.')
        user = User(username=username, is_staff=True)
        try:
            user.full_clean(exclude=['password'])
            validate_password(password, user=user)
        except ValidationError as exc:
            raise CommandError(' '.join(exc.messages))
        user.set_password(password)
        user.save()
        user.groups.add(Group.objects.get(name='Level editors'))
        self.stdout.write(self.style.SUCCESS('Level editor created. Log in at /admin/.'))
