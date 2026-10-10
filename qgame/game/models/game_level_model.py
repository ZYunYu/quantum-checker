from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

from ..game_logic import CIRCLE_PAULIS, QuantumGame, validate_gates


class CustomFloatField(models.FloatField):
    def __init__(self, *args, **kwargs):
        kwargs['null'] = True
        kwargs['blank'] = True
        kwargs['validators'] = [MinValueValidator(0.0), MaxValueValidator(1.0)]
        super().__init__(*args, **kwargs)


class GameLevel(models.Model):
    level = models.PositiveIntegerField(unique=True, validators=[MinValueValidator(1)])
    title = models.CharField(max_length=120, blank=True)
    instructions = models.TextField(blank=True)
    initial_gates = models.JSONField(default=list, blank=True)
    circle11 = CustomFloatField(verbose_name='Left qubit · Z (1,1)')
    circle12 = CustomFloatField(verbose_name='Left qubit · X (1,2)')
    circle21 = CustomFloatField(verbose_name='Correlation · ZX (2,1)')
    circle22 = CustomFloatField(verbose_name='Correlation · XX (2,2)')
    circle23 = CustomFloatField(verbose_name='Right qubit · X (2,3)')
    circle31 = CustomFloatField(verbose_name='Correlation · ZZ (3,1)')
    circle32 = CustomFloatField(verbose_name='Correlation · XZ (3,2)')
    circle33 = CustomFloatField(verbose_name='Right qubit · Z (3,3)')
    gate_z = models.BooleanField(default=False)
    gate_h = models.BooleanField(default=False)
    gate_x = models.BooleanField(default=False)
    gate_cz = models.BooleanField(default=False)
    win_conditions = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ['level']

    @property
    def allowed_gates(self):
        return [gate for gate in ('x', 'z', 'h', 'cz') if getattr(self, f'gate_{gate}')]

    def clean(self):
        super().clean()
        try:
            validate_gates(self.initial_gates)
        except ValueError as exc:
            raise ValidationError({'initial_gates': str(exc)})
        if not isinstance(self.win_conditions, list):
            raise ValidationError({'win_conditions': 'Use a list of conditions, or [] for no extra conditions.'})
        for item in self.win_conditions:
            valid = isinstance(item, dict)
            field = f"circle{item.get('row')}{item.get('column')}" if valid else ''
            values = [item['exact']] if valid and 'exact' in item else [item.get('min'), item.get('max')] if valid else []
            if field not in CIRCLE_PAULIS or not values or any(type(value) not in (int, float) or not 0 <= value <= 1 for value in values):
                raise ValidationError({'win_conditions': 'Each condition needs a valid row/column and exact, or min/max, between 0 and 1.'})
            if len(values) == 2 and values[0] > values[1]:
                raise ValidationError({'win_conditions': 'min must not be greater than max.'})
        if not any(getattr(self, field) is not None for field in CIRCLE_PAULIS) and not self.win_conditions:
            raise ValidationError('Set at least one target circle.')
        # The real two-qubit Clifford state space is small: check that the puzzle is solvable.
        queue = [QuantumGame(self.initial_gates).state]
        seen = set()
        while queue:
            game = QuantumGame()
            game.state = queue.pop(0)
            sign = next((1 if value > 0 else -1 for value in game.state if abs(value) > 1e-8), 1)
            key = tuple(round(value * sign, 8) for value in game.state)
            if key in seen:
                continue
            seen.add(key)
            if game.check_win(self):
                return
            for gate in self.allowed_gates:
                for bit in ((0,) if gate == 'cz' else (0, 1)):
                    successor = QuantumGame()
                    successor.state = list(game.state)
                    successor.apply_gate(bit, gate)
                    queue.append(successor.state)
        raise ValidationError('目标状态无法通过允许的量子门达到，请检查目标圆点和允许使用的门。')

    def __str__(self):
        return f"Level {self.level}" + (f" — {self.title}" if self.title else '')
