from django.db import models
from django.db.models import JSONField

class User(models.Model):
    name = models.CharField(max_length=50)
    rank = models.IntegerField()
    level = models.CharField(max_length=20)

class Problem(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    desc = models.CharField(max_length=200, default=None)
    difficulty = models.CharField(max_length=20)
    hashes = JSONField()
    inputs = JSONField()
    date_created = models.DateField()

class Submission(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    problem_id = models.ForeignKey(Problem, on_delete=models.CASCADE)
    analysis = JSONField()
    date_submitted = models.DateField()
