# Generated by Django 3.1.5 on 2021-03-18 22:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('code_analysis', '0007_problem_data'),
    ]

    operations = [
        migrations.RenameField(
            model_name='problem',
            old_name='data',
            new_name='supplied_data',
        ),
    ]
