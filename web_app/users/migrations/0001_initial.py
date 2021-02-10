# Generated by Django 3.1.5 on 2021-02-06 16:14

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('problem_id', models.IntegerField()),
                ('analysis', models.JSONField()),
                ('date_submitted', models.DateField()),
            ],
        ),
    ]