from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=None)
    rank = models.IntegerField(null=True)
    level = models.CharField(max_length=20, default="Beginner")
    about = models.CharField(max_length=200, null=True)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(user=instance)
        print(profile)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    print(instance)
    instance.profile.save()
