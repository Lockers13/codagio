# Generated by Django 3.1.5 on 2021-02-20 18:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('code_analysis', '0003_auto_20210220_1815'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='problem',
            unique_together=set(),
        ),
    ]
