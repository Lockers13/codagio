# Generated by Django 3.1.5 on 2021-02-20 18:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0017_auto_20210215_1459'),
        ('code_analysis', '0002_auto_20210220_1750'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='problem',
            unique_together={('name', 'author')},
        ),
    ]