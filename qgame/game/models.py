from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.db.models import JSONField


class CustomFloatField(models.FloatField):
    def __init__(self, *args, **kwargs):
        kwargs['null'] = True
        kwargs['blank'] = True
        kwargs['validators'] = [MinValueValidator(0.0), MaxValueValidator(1.0)]
        super().__init__(*args, **kwargs)


class GameLevel(models.Model):
    level = models.IntegerField(unique=True)
    circle11 = CustomFloatField()
    circle12 = CustomFloatField()
    circle21 = CustomFloatField()
    circle22 = CustomFloatField()
    circle23 = CustomFloatField()
    circle31 = CustomFloatField()
    circle32 = CustomFloatField()
    circle33 = CustomFloatField()
    gate_z = models.BooleanField(default=False)
    gate_h = models.BooleanField(default=False)
    gate_x = models.BooleanField(default=False)
    gate_cz = models.BooleanField(default=False)
    win_conditions = JSONField(default=dict, blank=True)
    # The expected format of win_conditions is:
    # [
    #   {"row": 1, "column": 1, "min": 0.8, "max": 1.0},
    #   {"row": 2, "column": 3, "min": 0.5, "max": 0.7},
    #   {"row": 3, "column": 3, "exact": 0.9}
    # ]

    def clean(self):
        # Verify the structure of win_conditions
        for condition in self.win_conditions:
            if not ("row" in condition and "column" in condition and ("min" in condition or "exact" in condition)):
                raise ValidationError("Invalid win condition structure.")

    def __str__(self):
        return f"Level {self.level}"
