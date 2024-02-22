from django.db import models
from django.contrib.auth.models import User
from .game_level_model import GameLevel

class UserGameLevel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game_level = models.ForeignKey(GameLevel, on_delete=models.CASCADE)


    class Meta:
        unique_together = (('user', 'game_level'),)

    def __str__(self):
        return f"{self.user.username} - Level {self.game_level.level}"
