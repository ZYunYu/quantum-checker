from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


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

    def __str__(self):
        return f"Level {self.level}"
