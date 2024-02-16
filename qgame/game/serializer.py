from rest_framework import serializers
from .models.game_level_model import GameLevel
from .models.game_session_model import GameSession


class GameLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameLevel
        fields = '__all__'

class GameSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameSession
        fields = ['session_id', 'game_level', 'current_state', 'applied_gates', 'probabilities', 'is_win']