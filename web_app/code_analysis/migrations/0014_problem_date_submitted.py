# Generated by Django 3.1.5 on 2021-03-21 18:49

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('code_analysis', '0013_remove_problem_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='problem',
            name='date_submitted',
            field=models.DateField(default=datetime.datetime(2021, 3, 21, 18, 49, 41, 215294)),
            preserve_default=False,
        ),
    ]
