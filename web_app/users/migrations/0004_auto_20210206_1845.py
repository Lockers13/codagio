# Generated by Django 3.1.5 on 2021-02-06 18:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_problem_desc'),
    ]

    operations = [
        migrations.AddField(
            model_name='problem',
            name='name',
            field=models.CharField(default=None, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='problem',
            name='desc',
            field=models.CharField(default=None, max_length=200, null=True),
        ),
    ]
