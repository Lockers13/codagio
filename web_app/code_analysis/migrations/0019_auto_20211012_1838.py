# Generated by Django 3.1.5 on 2021-10-12 18:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('code_analysis', '0018_solution_course'),
    ]

    operations = [
        migrations.AlterField(
            model_name='solution',
            name='submitter',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
