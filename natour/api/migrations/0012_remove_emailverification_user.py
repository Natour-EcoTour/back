# Generated by Django 5.2.3 on 2025-07-03 19:11
# pylint: skip-file

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_emailverification'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='emailverification',
            name='user',
        ),
    ]
