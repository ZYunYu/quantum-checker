from django.contrib import admin
from django.db import models
from django_json_widget.widgets import JSONEditorWidget
from .models import GameLevel

@admin.register(GameLevel)
class GameLevelAdmin(admin.ModelAdmin):
    list_display = ('level', 'circle11', 'circle12', 'circle21', 'circle22', 'circle23', 'circle31', 'circle32', 'circle33', 'display_gates')
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

