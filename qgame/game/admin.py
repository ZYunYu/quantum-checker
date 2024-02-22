from django.contrib import admin
from django.db import models
from django_json_widget.widgets import JSONEditorWidget
from .models.game_level_model import GameLevel
from .models.game_session_model import GameSession




@admin.register(GameLevel)
class GameLevelAdmin(admin.ModelAdmin):
    list_display = (
    'level', 'circle11', 'circle12', 'circle21', 'circle22', 'circle23', 'circle31', 'circle32', 'circle33',
    'display_gates')
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }

    def display_gates(self, obj):
        gates = []
        if obj.gate_z: gates.append('Gate Z')
        if obj.gate_h: gates.append('Gate H')
        if obj.gate_x: gates.append('Gate X')
        if obj.gate_cz: gates.append('Gate CZ')
        return ', '.join(gates)

    display_gates.short_description = 'Gates'


@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = (
        'display_user', 'display_game_level', 'display_current_state',
        'display_applied_gates', 'display_probabilities', 'is_win')

    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }

    def display_user(self, obj):
        return obj.user.username
    display_user.short_description = 'User'

    def display_game_level(self, obj):
        return f"Level {obj.game_level.level}"
    display_game_level.short_description = 'Game Level'

    def display_current_state(self, obj):
        return str(obj.current_state)
    display_current_state.short_description = 'Current State'

    def display_applied_gates(self, obj):
        return str(obj.applied_gates)
    display_applied_gates.short_description = 'Applied Gates'

    def display_probabilities(self, obj):
        return str(obj.probabilities)
    display_probabilities.short_description = 'Probabilities'
