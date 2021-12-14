# Generated by Django 3.1.5 on 2021-10-24 17:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classes', '0004_auto_20211009_1840'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='hash_digest',
            field=models.CharField(max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='course',
            name='code',
            field=models.CharField(max_length=100, null=True, unique=True),
        ),
    ]