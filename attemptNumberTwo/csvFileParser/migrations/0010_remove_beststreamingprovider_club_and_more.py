# Generated by Django 5.1.2 on 2024-12-30 17:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('csvFileParser', '0009_beststreamingprovider'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='beststreamingprovider',
            name='club',
        ),
        migrations.RemoveField(
            model_name='beststreamingprovider',
            name='streaming_package',
        ),
        migrations.DeleteModel(
            name='db_cache',
        ),
        migrations.AddField(
            model_name='streaming_package',
            name='annual_only',
            field=models.BooleanField(default=False, null=True),
        ),
        migrations.DeleteModel(
            name='BestStreamingProvider',
        ),
    ]
