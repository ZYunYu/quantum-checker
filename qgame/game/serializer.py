from rest_framework import serializers
from .models.game_level_model import GameLevel
from .models.game_session_model import GameSession


class GameLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameLevel
        fields = '__all__'

class GameSessionSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    game_level = serializers.SlugRelatedField(slug_field='level', queryset=GameLevel.objects.all())

    class Meta:
        model = GameSession
        fields = ['id', 'user', 'game_level', 'current_state', 'applied_gates', 'probabilities', 'is_win']

    def create(self, validated_data):
        return GameSession.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.current_state = validated_data.get('current_state', instance.current_state)
        instance.applied_gates = validated_data.get('applied_gates', instance.applied_gates)
        instance.probabilities = validated_data.get('probabilities', instance.probabilities)
        instance.is_win = validated_data.get('is_win', instance.is_win)
        instance.save()
        return instance
