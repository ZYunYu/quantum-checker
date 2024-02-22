from django.db import models
from .game_level_model import GameLevel
from django.contrib.auth.models import User

class GameSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game_level = models.ForeignKey(GameLevel, on_delete=models.CASCADE)
    current_state = models.JSONField(default=dict)
    applied_gates = models.JSONField(default=list)
    probabilities = models.JSONField(default=dict)
    is_win = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'game_level')

    def __str__(self):
        return f"Session for {self.user.username} (Level {self.game_level.level})"
