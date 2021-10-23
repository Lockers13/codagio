from django.db import models
from django.db.models import JSONField
from users.models import Profile
from classes.models import Course
from django.contrib.auth.models import User

class Problem(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, default=None)
    metadata = JSONField(default=dict)
    outputs = JSONField()
    inputs = JSONField(null=True)
    analysis = JSONField(default=dict)
    init_data = JSONField(null=True)
    date_submitted = models.DateField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)

class Solution(models.Model):
    submitter = models.ForeignKey(User, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    analysis = JSONField()
    date_submitted = models.DateTimeField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)
    
    class Meta:
        unique_together = ('submitter', 'problem',  'course_id', 'date_submitted')
