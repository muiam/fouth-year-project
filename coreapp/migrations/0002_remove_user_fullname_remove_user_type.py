# Generated by Django 4.0.6 on 2023-05-12 05:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coreapp', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='fullname',
        ),
        migrations.RemoveField(
            model_name='user',
            name='type',
        ),
    ]
