# Generated by Django 3.1.5 on 2021-04-13 16:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0017_auto_20210215_1459'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='about',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
