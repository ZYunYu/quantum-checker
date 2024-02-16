from django.db import models
from .game_level_model import GameLevel
import uuid

class GameSession(models.Model):
    session_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    game_level = models.ForeignKey(GameLevel, on_delete=models.CASCADE)
    current_state = models.JSONField(default=dict)  # Stores the current state of the qubit
    applied_gates = models.JSONField(default=list)  # Stores applied quantum gate operations
    probabilities = models.JSONField(default=dict)  # Store the current probability distribution
    is_win = models.BooleanField(default=False)

    def __str__(self):
        return f"Session {self.session_id} (Level {self.level})"
