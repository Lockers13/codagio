# Generated by Django 3.1.5 on 2021-02-11 16:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_auto_20210211_1609'),
    ]

    operations = [
        migrations.RenameField(
            model_name='solution',
            old_name='problem_id',
            new_name='problem',
        ),
        migrations.RenameField(
            model_name='solution',
            old_name='user_id',
            new_name='user',
        ),
        migrations.AlterUniqueTogether(
            name='solution',
            unique_together={('user', 'problem')},
        ),
    ]
