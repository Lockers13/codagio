# Generated by Django 3.1.5 on 2021-02-11 11:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20210207_1928'),
    ]

    operations = [
        migrations.AddField(
            model_name='problem',
            name='analysis',
            field=models.JSONField(default=''),
        ),
    ]
