# Generated by Django 3.2.10 on 2023-04-13 13:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coreapp', '0010_auto_20230413_1540'),
    ]

    operations = [
        migrations.AddField(
            model_name='requests',
            name='paykey',
            field=models.CharField(blank=True, max_length=6, null=True),
        ),
    ]
