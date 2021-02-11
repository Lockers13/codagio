from django.db import models
from django.db.models import JSONField

class User(models.Model):
    name = models.CharField(max_length=50)
    rank = models.IntegerField()
    level = models.CharField(max_length=20)

class Problem(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, default=None)
    desc = models.CharField(max_length=200, default=None, null=True)
    difficulty = models.CharField(max_length=20)
    hashes = JSONField()
    inputs = JSONField()
    date_created = models.DateField()
    analysis = JSONField(default=dict)

class Solution(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    analysis = JSONField()
    date_submitted = models.DateField()
    
    class Meta:
        unique_together = ('user', 'problem',)
