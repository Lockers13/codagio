# Generated by Django 3.1.5 on 2021-02-14 15:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0014_auto_20210214_1459'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='level',
            field=models.CharField(default='Beginner', max_length=20),
        ),
        migrations.AlterField(
            model_name='profile',
            name='rank',
            field=models.IntegerField(default=None),
        ),
    ]
