# Generated by Django 3.1.5 on 2021-10-12 18:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('classes', '0004_auto_20211009_1840'),
        ('code_analysis', '0017_auto_20211008_2219'),
    ]

    operations = [
        migrations.AddField(
            model_name='solution',
            name='course',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='classes.course'),
        ),
    ]
