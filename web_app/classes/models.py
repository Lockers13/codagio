from django.db import models
from django.contrib.auth.models import User

DIGEST_LEN = 64

class Course(models.Model):
    name = models.CharField(max_length=50, null=True)
    tutor = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=500, null=True)
    code = models.CharField(max_length=100, unique=True, null=True)
    hash_digest = models.CharField(max_length=DIGEST_LEN*2, null=True) # two hex chars per byte

class Enrolment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('student', 'course')
 