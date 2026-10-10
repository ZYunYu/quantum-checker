from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from .game_level_model import GameLevel


class Classroom(models.Model):
    name = models.CharField('班级名称', max_length=120, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = '班级'
        verbose_name_plural = '班级'

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(
        '学号', max_length=64, unique=True, null=True, blank=True,
        validators=[RegexValidator(r'^[A-Za-z0-9_-]+$', '学号只能包含数字、英文字母、下划线和连字符。')],
        help_text='按文本保存，保留开头的零；学号不能重复。管理员和旧账号可暂时留空。',
    )
    classroom = models.ForeignKey(
        Classroom, verbose_name='班级', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='students',
    )

    class Meta:
        verbose_name = '学生资料'
        verbose_name_plural = '学生资料'

    def clean(self):
        super().clean()
        self.student_id = self.student_id.strip() or None if self.student_id else None

    def __str__(self):
        return f'{self.user.username} ({self.student_id or "未填写学号"})'

class UserGameLevel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game_level = models.ForeignKey(GameLevel, on_delete=models.CASCADE)


    class Meta:
        unique_together = (('user', 'game_level'),)

    def __str__(self):
        return f"{self.user.username} - Level {self.game_level.level}"
