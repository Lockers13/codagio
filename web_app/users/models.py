from django.db import models
from django.db.models import JSONField
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=None)
    rank = models.IntegerField(null=True)
    level = models.CharField(max_length=20, default="Beginner")

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Problem(models.Model):
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, default=None)
    desc = models.CharField(max_length=200, default=None, null=True)
    difficulty = models.CharField(max_length=20)
    hashes = JSONField()
    inputs = JSONField()
    date_created = models.DateField()
    analysis = JSONField(default=dict)

class Solution(models.Model):
    submitter = models.ForeignKey(Profile, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    analysis = JSONField()
    date_submitted = models.DateField()
    
    class Meta:
        unique_together = ('submitter', 'problem',)
