from django.core.management.base import BaseCommand
from game.demo_levels import demo_levels
from game.models import GameLevel


class Command(BaseCommand):
    help = 'Add four original demo puzzles without overwriting existing levels.'

    def handle(self, *args, **options):
        for data in demo_levels():
            if GameLevel.objects.filter(level=data['level']).exists():
                continue
            level = GameLevel(**data)
            level.full_clean()
            level.save()
        self.stdout.write(self.style.SUCCESS('Demo levels are ready. Existing levels were preserved.'))
