from django.db import models
from django.contrib.auth.models import User

class Course(models.Model):
    name = models.CharField(max_length=50, null=True)
    tutor = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=500, null=True)
    code = models.CharField(max_length=100, null=True, default="courseX", unique=True)

class Enrolment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
 