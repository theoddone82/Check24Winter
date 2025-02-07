# Generated by Django 5.1.2 on 2024-11-01 13:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='game',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('team_home', models.CharField(max_length=100)),
                ('team_away', models.CharField(max_length=100)),
                ('starts_at', models.DateTimeField()),
                ('tournament_name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='streaming_package',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('monthly_price_cents', models.IntegerField()),
                ('monthly_price_yearly_subscription_cents', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='streaming_offer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('live', models.BooleanField()),
                ('highlights', models.BooleanField()),
                ('game_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='csvFileParser.game')),
                ('streaming_package_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='csvFileParser.streaming_package')),
            ],
        ),
    ]
