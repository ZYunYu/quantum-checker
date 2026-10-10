from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from .game_level_model import GameLevel


class Classroom(models.Model):
    name = models.CharField('Classroom name', max_length=120, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Classroom'
        verbose_name_plural = 'Classrooms'

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(
        'Student ID', max_length=64, unique=True, null=True, blank=True,
        validators=[RegexValidator(r'\AD[0-9]+\Z', 'Student ID must start with uppercase D followed by digits only, for example D00123456.')],
        help_text='Use uppercase D followed by digits only, for example D00123456. IDs must be unique; leading zeros are preserved. Administrators and existing accounts may leave this blank.',
    )
    classroom = models.ForeignKey(
        Classroom, verbose_name='Classroom', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='students',
    )

    class Meta:
        verbose_name = 'Student profile'
        verbose_name_plural = 'Student profiles'

    def clean(self):
        super().clean()
        self.student_id = self.student_id.strip() or None if self.student_id else None

    def __str__(self):
        return f'{self.user.username} ({self.student_id or "No student ID"})'

class UserGameLevel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game_level = models.ForeignKey(GameLevel, on_delete=models.CASCADE)


    class Meta:
        unique_together = (('user', 'game_level'),)

    def __str__(self):
        return f"{self.user.username} - Level {self.game_level.level}"
