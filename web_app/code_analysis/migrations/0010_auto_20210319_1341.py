# Generated by Django 3.1.5 on 2021-03-19 13:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('code_analysis', '0009_auto_20210318_2226'),
    ]

    operations = [
        migrations.RenameField(
            model_name='problem',
            old_name='supplied_data',
            new_name='init_data',
        ),
    ]
