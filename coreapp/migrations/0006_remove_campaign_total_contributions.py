# Generated by Django 4.0.6 on 2023-05-17 17:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coreapp', '0005_alter_campaign_owner'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='campaign',
            name='total_contributions',
        ),
    ]