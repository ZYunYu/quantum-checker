from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserProfile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_student_profile(sender, instance, created, raw=False, using=None, **kwargs):
    if created and not raw:
        UserProfile.objects.using(using).get_or_create(user_id=instance.pk)
