from django.core.exceptions import ValidationError
from rest_framework import serializers
from .models.game_level_model import GameLevel


class GameLevelSerializer(serializers.ModelSerializer):
    allowed_gates = serializers.ReadOnlyField()

    class Meta:
        model = GameLevel
        fields = '__all__'

    def validate(self, attrs):
        level = GameLevel(**attrs)
        try:
            level.full_clean()
        except ValidationError as exc:
            raise serializers.ValidationError(exc.message_dict)
        return attrs
